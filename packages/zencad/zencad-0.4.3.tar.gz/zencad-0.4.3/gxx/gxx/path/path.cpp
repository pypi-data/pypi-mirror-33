#include <gxx/path/path.h>
#include <gxx/creader.h>

#include <gxx/debug/dprint.h>

std::string gxx::path::dirname(const std::string& path) {
	const char* strt = path.c_str();
	const char* ptr = strt;
	const char* last = strt;

	gxx::chars_set_checker pattern("/\\");

	while(*ptr) {
		if (pattern(*ptr)) last = ptr;
		++ptr;
	} 

	return std::string(strt, last - strt);
}
