#include <gxx/syslock.h>
#include <mutex>

std::recursive_mutex mtx;

void gxx::syslock::lock() {
	mtx.lock();
}

void gxx::syslock::unlock() {
	mtx.unlock();
}