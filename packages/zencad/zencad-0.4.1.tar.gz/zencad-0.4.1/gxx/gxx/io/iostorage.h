#ifndef GXX_IO_OBUFFER_H
#define GXX_IO_OBUFFER_H

#include <gxx/io/iostream.h>
#include <gxx/event/delegate.h>

namespace gxx {
	namespace io {
		/*class ostorage : public gxx::io::ostream {
		public:
			virtual int room() = 0;
			virtual void set_empty_callback(gxx::delegate<void> dlg) {};
		};

		class istorage : public gxx::io::istream {
		public:
			virtual int avail() = 0;
		};

		class iostorage : public gxx::io::ostorage, public gxx::io::istorage {}; 
		*/
	}
}

#endif