#ifndef GXX_CRITICAL_SECTION_H
#define GXX_CRITICAL_SECTION_H

namespace gxx {
	struct atomic_section {
		void lock();
		void unlock();
	};
} 

#endif