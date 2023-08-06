#ifndef GXX_DEBUG_OSTREAM_H
#define GXX_DEBUG_OSTREAM_H

#include <iostream>

namespace gxx {
	namespace io {
		class debug_streambuf : public std::streambuf {
			int overflow(int c) override {
				debug_putchar(c);
				return c;
			}
	
			int underflow() override {
				abort();
			}
	
			int uflow() override {
				abort();
			}
		};

		class debug_ostream : public std::ostream {
			debug_streambuf ddd;
		public:
			debug_ostream() : std::ostream(&ddd) {}
		};
	}
}

#endif