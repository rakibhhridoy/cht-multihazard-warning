/* macOS shim: no libnuma. Used only to print each thread's NUMA node (lisflood_processing.cpp). */
#pragma once
static inline int numa_node_of_cpu(int) { return 0; }
static inline int sched_getcpu(void) { return 0; }
