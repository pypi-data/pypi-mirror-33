#ifndef GXX_DEBUG_FUNCTIONS_H
#define GXX_DEBUG_FUNCTIONS_H

#include <gxx/debug/debug_ostream.h>
#include <gxx/print.h>

namespace gxx {
	template<typename ... Args>
	void debug(Args ... args) {
		debug_ostream dout;
		dout.print("gxx::debug: ");
		gxx::fprint_to(dout, std::forward<Args>(args) ...);
	}
}

#endif