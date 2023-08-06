#include <stdint.h>
#include <gxx_configure.h>

void debug_delay(uint32_t ms) {
	volatile uint64_t a = ms * GXX_DELAY_MULTIPLIER;
	while(a--);
}