#ifndef GXX_RINGSTREAM_H
#define GXX_RINGSTREAM_H

#include <gxx/bytering.h>
#include <gxx/io/strm.h>
#include <gxx/buffer.h>

namespace gxx {
	namespace io {
		class ringstrm : public lstrmio {
			gxx::bytering ring;

		public:
			ringstrm(gxx::buffer buf) : ring(buf) {};

			int write(const char* str, size_t sz) override {
				return ring.write(str, sz);
			}

			int read(char* str, size_t sz) override {
				return ring.read(str, sz);
			}

			size_t room() override {
				return ring.room();
			}

			size_t avail() override {
				return ring.avail();
			}
		};
	}
}

#endif