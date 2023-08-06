#ifndef GXX_CSECTION_H
#define GXX_CSECTION_H

namespace gxx {
	struct syslock {
		void lock();
		void unlock();
	};

	static inline void system_lock() { syslock().lock(); }
	static inline void system_unlock() { syslock().unlock(); }
}

#endif