#ifndef GXX_IO_DGRAMM_H
#define GXX_IO_DGRAMM_H

#include <stdlib.h>

namespace gxx { namespace io {
	class dgrammer {
		virtual void send_datagramm(const char* data, size_t size) = 0;
		virtual void read_datagramm(char* data, size_t maxsize) = 0;
	};
}}

#endif