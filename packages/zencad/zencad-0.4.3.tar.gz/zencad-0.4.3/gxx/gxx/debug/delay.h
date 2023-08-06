#ifndef GXX_DEBUG_DELAY_H
#define GXX_DEBUG_DELAY_H

#include <stdint.h>
#include <sys/cdefs.h>

__BEGIN_DECLS

static double __debug_delay_multiplier = 1;

static inline void debug_simple_delay(uint64_t ticks) {
	volatile uint64_t count = ticks;
	while(count--);
}

static void debug_delay(uint32_t ms) {
	debug_simple_delay(ms * __debug_delay_multiplier);
}

__END_DECLS

#endif