#include <gxx/syslock.h>
#include <genos/hal/irqs.h>

static arch::irqs::save_t save;
static int count = 0;

void gxx::syslock::lock() {
	if (count == 0) save = genos::hal::irqs::save();
	++count;
}

void gxx::syslock::unlock() {
	--count;
	if (count == 0) genos::hal::irqs::restore(save);
}