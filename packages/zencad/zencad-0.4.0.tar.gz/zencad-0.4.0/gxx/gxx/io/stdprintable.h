#ifndef GXX_IO_STDPRINTABLE_H
#define GXX_IO_STDPRINTABLE_H

#include <gxx/io/ostream.h>
#include <gxx/io/printable.h>
#include <vector>

namespace gxx {
	namespace io {
		template<typename T>
		class printable_helper_vector : public gxx::io::printable {
		public:
			printable_helper_vector(const std::vector<T>& vec) {}

			size_t printTo(gxx::io::ostream& out) const override {
				dprln("here");
			}
		};
	}
}

#endif