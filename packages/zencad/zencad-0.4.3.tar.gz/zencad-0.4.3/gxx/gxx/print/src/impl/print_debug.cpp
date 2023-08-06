#include <gxx/print.h>
#include <gxx/debug/debug_ostream.h>

static gxx::debug_ostream out;

namespace gxx {
	gxx::io::ostream* standart_output = &out;
}