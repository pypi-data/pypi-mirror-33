#ifndef GXX_IO_READER_H
#define GXX_IO_READER_H

namespace gxx {
	class reader {
		virtual size_t read(char* data, size_t size) = 0;
	};
}

#endif