#ifndef GXX_OSTREAM_MESSENGER_H
#define GXX_OSTREAM_MESSENGER_H

#include <gxx/io/ostream.h>

namespace gxx {
	namespace io {
		class ostream_messenger : public gxx::io::ostream {
			virtual void start_message() = 0;
			virtual void end_message() = 0;
		};
	}
}

#endif // OSTREAM_MESSENGER_H
