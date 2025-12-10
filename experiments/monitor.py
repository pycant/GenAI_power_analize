import time
import threading
import psutil

class ResourceMonitor:
    def __init__(self, interval=0.2):
        self.interval = interval
        self._stop = threading.Event()
        self._thread = None
        self.timestamps = []
        self.cpu_percent = []
        self.mem_used_mb = []
        self.disk_read_bytes = []
        self.disk_write_bytes = []
        self.gpu_util = []
        self.gpu_mem_mb = []
        self.gpu_power_w = []
        self.gpu_energy_j = 0.0
        self.gpu_temp_c = []
        self.gpu_processes = []
        self.cpu_proc_percent = []
        self.cpu_power_w_approx = []
        self.cpu_energy_j_approx = 0.0

    def start(self):
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join()

    def _sample_gpu(self):
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            power_mw = 0
            try:
                power_mw = pynvml.nvmlDeviceGetPowerUsage(handle)
            except:
                power_mw = 0
            temp_c = 0
            try:
                temp_c = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            except:
                temp_c = 0
            procs = []
            try:
                try:
                    plist = pynvml.nvmlDeviceGetComputeRunningProcesses_v2(handle)
                except:
                    plist = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
                for p in plist:
                    used_mb = 0
                    try:
                        used_mb = getattr(p, 'usedGpuMemory', 0) / 1024 / 1024
                    except:
                        used_mb = 0
                    procs.append({"pid": getattr(p, 'pid', None), "used_gpu_memory_mb": used_mb})
            except:
                procs = []
            return util.gpu, mem.used / 1024 / 1024, power_mw / 1000.0, temp_c, procs
        except:
            return None, None, None, None, []

    def _loop(self):
        last_ts = None
        last_read = None
        last_write = None
        while not self._stop.is_set():
            ts = time.time()
            self.timestamps.append(ts)
            self.cpu_percent.append(psutil.cpu_percent(interval=None))
            vm = psutil.virtual_memory()
            self.mem_used_mb.append((vm.total - vm.available) / 1024 / 1024)
            dio = psutil.disk_io_counters()
            rb = dio.read_bytes
            wb = dio.write_bytes
            if last_read is None:
                self.disk_read_bytes.append(0)
            else:
                self.disk_read_bytes.append(max(0, rb - last_read))
            if last_write is None:
                self.disk_write_bytes.append(0)
            else:
                self.disk_write_bytes.append(max(0, wb - last_write))
            last_read = rb
            last_write = wb
            gu, gm, pw, tc, procs = self._sample_gpu()
            if gu is not None:
                self.gpu_util.append(gu)
                self.gpu_mem_mb.append(gm)
                self.gpu_power_w.append(pw)
                self.gpu_temp_c.append(tc)
                self.gpu_processes.append(procs)
            else:
                self.gpu_util.append(0)
                self.gpu_mem_mb.append(0)
                self.gpu_power_w.append(0)
                self.gpu_temp_c.append(0)
                self.gpu_processes.append([])
            if last_ts is not None:
                dt = ts - last_ts
                self.gpu_energy_j += (self.gpu_power_w[-1]) * dt
                tdp = 65.0
                try:
                    tdp = float(os.environ.get("CPU_TDP_W", "65"))
                except:
                    tdp = 65.0
                pwr = (self.cpu_percent[-1] / 100.0) * tdp
                self.cpu_power_w_approx.append(pwr)
                self.cpu_energy_j_approx += pwr * dt
            last_ts = ts
            try:
                proc_sum = 0.0
                for p in psutil.process_iter(["pid", "name"]):
                    name = p.info.get("name") or ""
                    if "ollama" in name.lower():
                        try:
                            proc_sum += p.cpu_percent(interval=None)
                        except:
                            pass
                self.cpu_proc_percent.append(proc_sum)
            except:
                self.cpu_proc_percent.append(0.0)
            time.sleep(self.interval)

    def summary(self):
        def avg(lst):
            return sum(lst) / len(lst) if lst else 0
        def peak(lst):
            return max(lst) if lst else 0
        return {
            "cpu_percent_avg": avg(self.cpu_percent),
            "cpu_percent_peak": peak(self.cpu_percent),
            "mem_used_peak_mb": peak(self.mem_used_mb),
            "gpu_util_avg": avg(self.gpu_util),
            "gpu_util_peak": peak(self.gpu_util),
            "gpu_mem_peak_mb": peak(self.gpu_mem_mb),
            "gpu_power_avg_w": avg(self.gpu_power_w),
            "gpu_energy_j": self.gpu_energy_j,
            "gpu_temp_peak_c": peak(self.gpu_temp_c),
            "cpu_energy_j_approx": self.cpu_energy_j_approx
        }

    def to_dict(self):
        return {
            "timestamps": self.timestamps,
            "cpu_percent": self.cpu_percent,
            "cpu_proc_percent": self.cpu_proc_percent,
            "mem_used_mb": self.mem_used_mb,
            "disk_read_bytes": self.disk_read_bytes,
            "disk_write_bytes": self.disk_write_bytes,
            "gpu_util": self.gpu_util,
            "gpu_mem_mb": self.gpu_mem_mb,
            "gpu_power_w": self.gpu_power_w,
            "gpu_temp_c": self.gpu_temp_c,
            "gpu_processes": self.gpu_processes,
            "gpu_energy_j": self.gpu_energy_j,
            "cpu_power_w_approx": self.cpu_power_w_approx,
            "cpu_energy_j_approx": self.cpu_energy_j_approx,
            "summary": self.summary()
        }
