import argparse
import time
import os
import csv
from datetime import datetime
import psutil
import pynvml

def init_nvml():
    try:
        pynvml.nvmlInit()
        return True
    except Exception:
        return False

def gpu_count():
    try:
        return pynvml.nvmlDeviceGetCount()
    except Exception:
        return 0

def read_gpu(i, pid=None):
    h = pynvml.nvmlDeviceGetHandleByIndex(i)
    name = pynvml.nvmlDeviceGetName(h)
    mem = pynvml.nvmlDeviceGetMemoryInfo(h)
    util = pynvml.nvmlDeviceGetUtilizationRates(h)
    temp = pynvml.nvmlDeviceGetTemperature(h, pynvml.NVML_TEMPERATURE_GPU)
    try:
        power = pynvml.nvmlDeviceGetPowerUsage(h) / 1000.0
    except Exception:
        power = 0.0
    try:
        sm_clock = pynvml.nvmlDeviceGetClockInfo(h, pynvml.NVML_CLOCK_SM)
        mem_clock = pynvml.nvmlDeviceGetClockInfo(h, pynvml.NVML_CLOCK_MEM)
    except Exception:
        sm_clock = 0
        mem_clock = 0
    pid_gpu_mem = None
    if pid:
        try:
            procs = pynvml.nvmlDeviceGetComputeRunningProcesses(h)
            for p in procs:
                if p.pid == pid:
                    pid_gpu_mem = round(p.usedGpuMemory/1024/1024, 2)
                    break
        except Exception:
            pid_gpu_mem = None
    return {
        "gpu_index": i,
        "gpu_name": name,
        "gpu_util": util.gpu,
        "mem_util": util.memory,
        "mem_used_mb": round(mem.used/1024/1024, 2),
        "mem_total_mb": round(mem.total/1024/1024, 2),
        "temp_c": temp,
        "power_w": round(power, 2),
        "sm_clock_mhz": sm_clock,
        "mem_clock_mhz": mem_clock,
        "pid_gpu_mem_mb": pid_gpu_mem
    }

def read_cpu(pid=None):
    cpu_percent = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()
    res = {
        "cpu_percent": cpu_percent,
        "ram_used_gb": round((ram.total - ram.available)/1024/1024/1024, 2)
    }
    if pid:
        try:
            p = psutil.Process(pid)
            res["pid_cpu_percent"] = p.cpu_percent(interval=None)
            res["pid_ram_gb"] = round(p.memory_info().rss/1024/1024/1024, 4)
        except Exception:
            res["pid_cpu_percent"] = None
            res["pid_ram_gb"] = None
    return res

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=float, default=0.5)
    ap.add_argument("--duration", type=float, default=30)
    ap.add_argument("--output", default="logs/sd_comfy_perf.csv")
    ap.add_argument("--pid", type=int, default=None)
    args = ap.parse_args()
    ok = init_nvml()
    if not ok:
        print("NVML init failed")
        return
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    gnum = gpu_count()
    t0 = time.time()
    header = [
        "ts","gpu_index","gpu_name","gpu_util","mem_util","mem_used_mb","mem_total_mb","temp_c","power_w","sm_clock_mhz","mem_clock_mhz","cpu_percent","ram_used_gb","pid_gpu_mem_mb","pid_cpu_percent","pid_ram_gb"
    ]
    peaks = {}
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        while True:
            now = datetime.now().isoformat()
            cpu = read_cpu(args.pid)
            for i in range(gnum):
                gpu = read_gpu(i, args.pid)
                row = [
                    now,
                    gpu["gpu_index"], gpu["gpu_name"], gpu["gpu_util"], gpu["mem_util"], gpu["mem_used_mb"], gpu["mem_total_mb"], gpu["temp_c"], gpu["power_w"], gpu["sm_clock_mhz"], gpu["mem_clock_mhz"],
                    cpu["cpu_percent"], cpu["ram_used_gb"], gpu["pid_gpu_mem_mb"], cpu.get("pid_cpu_percent"), cpu.get("pid_ram_gb")
                ]
                w.writerow(row)
                k = f"gpu{i}"
                pk = peaks.get(k, {"gpu_util":0,"mem_used_mb":0,"power_w":0,"temp_c":0})
                pk["gpu_util"] = max(pk["gpu_util"], gpu["gpu_util"])
                pk["mem_used_mb"] = max(pk["mem_used_mb"], gpu["mem_used_mb"])
                pk["power_w"] = max(pk["power_w"], gpu["power_w"])
                pk["temp_c"] = max(pk["temp_c"], gpu["temp_c"])
                peaks[k] = pk
            time.sleep(args.interval)
            if time.time() - t0 >= args.duration:
                break
    for i in range(gnum):
        k = f"gpu{i}"
        pk = peaks.get(k, {})
        print("gpu", i, "peak_util", pk.get("gpu_util"), "peak_mem_mb", pk.get("mem_used_mb"), "peak_power_w", pk.get("power_w"), "peak_temp_c", pk.get("temp_c"))

if __name__ == "__main__":
    main()
