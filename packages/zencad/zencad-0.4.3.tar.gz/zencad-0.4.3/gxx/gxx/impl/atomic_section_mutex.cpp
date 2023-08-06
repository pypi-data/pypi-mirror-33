#include <gxx/atomic_section.h>
#include <mutex>

std::recursive_mutex atomic_mtx;

void gxx::atomic_section::lock() {
	atomic_mtx.lock();
}

void gxx::atomic_section::unlock() {
	atomic_mtx.unlock();
}