#ifndef GXX_IO_BASE_H
#define GXX_IO_BASE_H

#include <stdlib.h>
#include <stdint.h>
#include <gxx/event/flag.h>

namespace gxx {
	namespace io {
		struct writer { virtual size_t write(const char* data, size_t size) = 0; };	
		struct reader { virtual size_t read(char* data, size_t size) = 0; };
		struct istorage : public reader { gxx::event::action_flag rx_avail; };
		struct ostorage : public writer { gxx::event::action_flag tx_empty; };
		struct iostorage : public istorage, public ostorage {};
	}
}

#endif