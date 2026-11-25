"""Đo một lệnh tốn bao nhiêu RAM, CPU, thời gian; có thể giả lập máy yếu (chỉ Windows).

    python -I -X utf8 cong-cu/do_may.py [--ram-gb 5] [--nhan 4] [--ghi do.json] -- <lệnh ...>

Chạy lệnh trong một Job Object của Windows: mọi tiến trình con (ffmpeg, node, Chrome của Remotion, Whisper) đều tính chung.
--ram-gb: trần bộ nhớ cam kết (commit) của cả nhóm. Vượt trần thì cấp phát thất bại, tức là khắt khe hơn máy thật
          (máy thật còn tệp hoán đổi nên chậm đi chứ chưa chắc hỏng). Máy 8 GB: Windows + Claude + trình duyệt chiếm
          khoảng 3 GB, nên thử với --ram-gb 5.
--nhan:   chỉ cho chạy trên N nhân logic đầu tiên.
In mỗi 2 giây: RAM đang dùng (tổng working set), RAM toàn máy còn trống. Cuối cùng in đỉnh RAM, thời gian, CPU.
"""
import argparse
import ctypes
import json
import subprocess
import sys
import time
from ctypes import wintypes as W

k32 = ctypes.WinDLL('kernel32', use_last_error=True)
psapi = ctypes.WinDLL('psapi', use_last_error=True)


class IO(ctypes.Structure):
    _fields_ = [(n, ctypes.c_ulonglong) for n in ('r_op', 'w_op', 'o_op', 'r_b', 'w_b', 'o_b')]


class BASIC(ctypes.Structure):
    _fields_ = [('PerProcessUserTimeLimit', ctypes.c_longlong), ('PerJobUserTimeLimit', ctypes.c_longlong),
                ('LimitFlags', W.DWORD), ('MinimumWorkingSetSize', ctypes.c_size_t), ('MaximumWorkingSetSize', ctypes.c_size_t),
                ('ActiveProcessLimit', W.DWORD), ('Affinity', ctypes.c_size_t), ('PriorityClass', W.DWORD), ('SchedulingClass', W.DWORD)]


class EXT(ctypes.Structure):
    _fields_ = [('Basic', BASIC), ('Io', IO), ('ProcessMemoryLimit', ctypes.c_size_t), ('JobMemoryLimit', ctypes.c_size_t),
                ('PeakProcessMemoryUsed', ctypes.c_size_t), ('PeakJobMemoryUsed', ctypes.c_size_t)]


class ACC(ctypes.Structure):
    _fields_ = [('TotalUserTime', ctypes.c_longlong), ('TotalKernelTime', ctypes.c_longlong), ('ThisPeriodTotalUserTime', ctypes.c_longlong),
                ('ThisPeriodTotalKernelTime', ctypes.c_longlong), ('TotalPageFaultCount', W.DWORD), ('TotalProcesses', W.DWORD),
                ('ActiveProcesses', W.DWORD), ('TotalTerminatedProcesses', W.DWORD)]


class PMC(ctypes.Structure):
    _fields_ = [('cb', W.DWORD), ('PageFaultCount', W.DWORD), ('PeakWorkingSetSize', ctypes.c_size_t), ('WorkingSetSize', ctypes.c_size_t),
                ('a', ctypes.c_size_t), ('b', ctypes.c_size_t), ('c', ctypes.c_size_t), ('d', ctypes.c_size_t),
                ('PagefileUsage', ctypes.c_size_t), ('PeakPagefileUsage', ctypes.c_size_t)]


class MEMSTAT(ctypes.Structure):
    _fields_ = [('dwLength', W.DWORD), ('dwMemoryLoad', W.DWORD), ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                ('a', ctypes.c_ulonglong), ('b', ctypes.c_ulonglong), ('c', ctypes.c_ulonglong), ('d', ctypes.c_ulonglong), ('e', ctypes.c_ulonglong)]


def ram_trong():
    m = MEMSTAT()
    m.dwLength = ctypes.sizeof(m)
    k32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys


def pid_trong_job(job):
    class L(ctypes.Structure):
        _fields_ = [('n', W.DWORD), ('m', W.DWORD), ('ids', ctypes.c_size_t * 4096)]
    l = L()
    k32.QueryInformationJobObject(job, 3, ctypes.byref(l), ctypes.sizeof(l), None)
    return list(l.ids[:l.m])


def working_set(pids):
    tong = 0
    for p in pids:
        h = k32.OpenProcess(0x1000 | 0x0010, False, p)  # QUERY_LIMITED_INFORMATION | VM_READ
        if not h:
            continue
        c = PMC()
        c.cb = ctypes.sizeof(c)
        if psapi.GetProcessMemoryInfo(h, ctypes.byref(c), c.cb):
            tong += c.WorkingSetSize
        k32.CloseHandle(h)
    return tong


def main():
    if '--' not in sys.argv:
        sys.exit(__doc__)
    i = sys.argv.index('--')
    ap = argparse.ArgumentParser()
    ap.add_argument('--ram-gb', type=float)
    ap.add_argument('--nhan', type=int)
    ap.add_argument('--ghi')
    a = ap.parse_args(sys.argv[1:i])
    lenh = sys.argv[i + 1:]

    k32.CreateJobObjectW.restype = W.HANDLE
    job = k32.CreateJobObjectW(None, None)
    e = EXT()
    co = 0x2000  # KILL_ON_JOB_CLOSE
    if a.ram_gb:
        co |= 0x200
        e.JobMemoryLimit = int(a.ram_gb * 2 ** 30)
    if a.nhan:
        co |= 0x10
        e.Basic.Affinity = (1 << a.nhan) - 1
    e.Basic.LimitFlags = co
    if not k32.SetInformationJobObject(job, 9, ctypes.byref(e), ctypes.sizeof(e)):
        sys.exit(f'Không đặt được giới hạn (lỗi {ctypes.get_last_error()})')

    bd = time.time()
    p = subprocess.Popen(lenh, creationflags=0x4)  # CREATE_SUSPENDED: gắn vào job trước khi chạy
    k32.OpenProcess.restype = W.HANDLE
    hp = k32.OpenProcess(0x1F0FFF, False, p.pid)
    if not k32.AssignProcessToJobObject(job, hp):
        p.kill()
        sys.exit(f'Không gắn được vào job (lỗi {ctypes.get_last_error()})')
    ntdll = ctypes.WinDLL('ntdll')
    ntdll.NtResumeProcess(hp)

    dinh_ws, thap_trong, mau = 0, ram_trong(), []
    while p.poll() is None:
        ws = working_set(pid_trong_job(job))
        tr = ram_trong()
        dinh_ws, thap_trong = max(dinh_ws, ws), min(thap_trong, tr)
        mau.append((round(time.time() - bd, 1), round(ws / 2 ** 30, 2)))
        if len(mau) % 5 == 1:
            print(f'[do_may] {mau[-1][0]:7.1f}s  RAM nhóm {ws / 2 ** 30:5.2f} GB  máy còn trống {tr / 2 ** 30:5.1f} GB', flush=True)
        time.sleep(2)
    giay = time.time() - bd
    ext, acc = EXT(), ACC()
    k32.QueryInformationJobObject(job, 9, ctypes.byref(ext), ctypes.sizeof(ext), None)
    k32.QueryInformationJobObject(job, 1, ctypes.byref(acc), ctypes.sizeof(acc), None)
    cpu = (acc.TotalUserTime + acc.TotalKernelTime) / 1e7
    kq = {'lenh': ' '.join(lenh)[:300], 'ma_thoat': p.returncode, 'giay': round(giay, 1),
          'dinh_ram_working_set_gb': round(dinh_ws / 2 ** 30, 2), 'dinh_ram_commit_gb': round(ext.PeakJobMemoryUsed / 2 ** 30, 2),
          'cpu_giay': round(cpu, 1), 'cpu_trung_binh_nhan': round(cpu / max(giay, 1), 2), 'so_tien_trinh': acc.TotalProcesses,
          'gioi_han': {'ram_gb': a.ram_gb, 'nhan': a.nhan}, 'ram_may_con_trong_thap_nhat_gb': round(thap_trong / 2 ** 30, 1), 'mau': mau}
    print('[do_may] ' + json.dumps({k: v for k, v in kq.items() if k != 'mau'}, ensure_ascii=False))
    if a.ghi:
        with open(a.ghi, 'w', encoding='utf-8') as f:
            json.dump(kq, f, ensure_ascii=False, indent=1)
    sys.exit(p.returncode)


if __name__ == '__main__':
    main()
