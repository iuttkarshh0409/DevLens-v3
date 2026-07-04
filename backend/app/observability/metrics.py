import time
from typing import Dict, Any, List

class MetricsRegistry:
    def __init__(self):
        self.counters: Dict[str, Dict[str, int]] = {}
        self.gauges: Dict[str, Dict[str, float]] = {}
        self.histograms: Dict[str, Dict[str, List[float]]] = {}
        
    def _format_labels(self, labels: Dict[str, Any]) -> str:
        if not labels:
            return ""
        items = [f'{k}="{v}"' for k, v in labels.items()]
        return "{" + ",".join(items) + "}"

    def increment(self, name: str, labels: Dict[str, Any] = None):
        lbl_str = self._format_labels(labels)
        if name not in self.counters:
            self.counters[name] = {}
        self.counters[name][lbl_str] = self.counters[name].get(lbl_str, 0) + 1

    def set_gauge(self, name: str, value: float, labels: Dict[str, Any] = None):
        lbl_str = self._format_labels(labels)
        if name not in self.gauges:
            self.gauges[name] = {}
        self.gauges[name][lbl_str] = value

    def observe(self, name: str, value: float, labels: Dict[str, Any] = None):
        lbl_str = self._format_labels(labels)
        if name not in self.histograms:
            self.histograms[name] = {}
        if lbl_str not in self.histograms[name]:
            self.histograms[name][lbl_str] = []
        self.histograms[name][lbl_str].append(value)

    def generate_prometheus_output(self) -> str:
        lines = []
        
        # 1. Output Counters
        for name, label_map in self.counters.items():
            lines.append(f"# HELP {name} counter description")
            lines.append(f"# TYPE {name} counter")
            for labels, value in label_map.items():
                lines.append(f"{name}{labels} {value}")
                
        # 2. Output Gauges
        for name, label_map in self.gauges.items():
            lines.append(f"# HELP {name} gauge description")
            lines.append(f"# TYPE {name} gauge")
            for labels, value in label_map.items():
                lines.append(f"{name}{labels} {value}")

        # 3. Output Histograms
        for name, label_map in self.histograms.items():
            lines.append(f"# HELP {name} histogram description")
            lines.append(f"# TYPE {name} histogram")
            for labels, values in label_map.items():
                count = len(values)
                total_sum = sum(values)
                # Output count and sum
                lines.append(f"{name}_count{labels} {count}")
                lines.append(f"{name}_sum{labels} {total_sum:.4f}")
                
                # Output custom buckets
                buckets = [0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
                for b in buckets:
                    b_count = sum(1 for v in values if v <= b)
                    # Insert le bucket label
                    if labels:
                        # Append to existing labels
                        lbls = labels[:-1] + f',le="{b}"' + "}"
                    else:
                        lbls = f'{lbls}' if 'lbls' in locals() else f'{{le="{b}"}}'
                    lines.append(f"{name}_bucket{lbls} {b_count}")
                    
                inf_lbls = labels[:-1] + ',le="+Inf"}' if labels else '{le="+Inf"}'
                lines.append(f"{name}_bucket{inf_lbls} {count}")
                
        return "\n".join(lines) + "\n"

# Global Shared Registry
metrics_registry = MetricsRegistry()
