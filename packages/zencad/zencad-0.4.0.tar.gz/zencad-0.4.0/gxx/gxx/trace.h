#ifndef GXX_TRACE_H
#define GXX_TRACE_H

#include <gxx/log/logger2.h>
#include <gxx/arglist.h>

using namespace gxx::argument_literal;

//gxx::log::logger* trace_log = nullptr;
uint8_t trace_level = 0;

namespace gxx {
//inline void set_trace_logger(gxx::log::logger* logger) {
//    trace_log = logger;
//}

struct tracer {
    const char* func = func;

    template <typename ... Args>
    tracer(const char* fmt, const char* func, Args&& ... args) {
        this->func = func;
        gxx::fprintln(fmt, trace_level, func);
        ++trace_level;
    }

    ~tracer() {
        --trace_level;
        gxx::fprintln("TRACE: {}: <- {}", trace_level, func);
    }
};
}

#if GXX_TRACE_ENABLE==1
#define GXX_TRACE() gxx::tracer __tracer("TRACE: {}: -> {}", __FUNCTION__)
#else
#define GXX_TRACE()
#endif

#endif
