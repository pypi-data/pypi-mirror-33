#include <gxx/io/std.h>
#include <gxx/util/init_priority.h>

namespace gxx { namespace io {
	gxx::io::std_ostream GXX_PRIORITY_INITIALIZATION_SUPER cout(std::cout);
	//gxx::io::std_ostream cerr(std::cerr.rdbuf());
	gxx::io::std_istream GXX_PRIORITY_INITIALIZATION_SUPER cin(std::cin);
}}
