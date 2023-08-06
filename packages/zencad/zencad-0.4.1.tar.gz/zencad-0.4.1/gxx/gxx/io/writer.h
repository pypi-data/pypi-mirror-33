#ifndef GXX_IO_WRITER_H
#define GXX_IO_WRITER_H

namespace gxx {
	class writer {
		virtual size_t write(const char* data, size_t size) = 0;
	};
}

#endif