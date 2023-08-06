#include <gxx/io/ostream.h>

int gxx::io::ostream::print(const char* fmt, const format_arglist& args) {
	print("format args");
	print(args[0]);
}