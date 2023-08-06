#ifndef GXX_MESSAGE_SERVICE_H
#define GXX_MESSAGE_SERVICE_H

#include <sys/cdefs.h>

typedef void (*oninput_t)(struct msg_t*);
typedef void (*onanswer_t)(struct msg_t*);
typedef service_id int;

struct msg_t {
	service_id sender;
	receiver_id sender;
	void* data;
	size_t size;
	void* rdata;
	size_t rsize;
	bool need_answer;
};

struct service_operations {
	oninput_t oninput;
	onanswer_t onanswer;
};

struct service_t {
	const struct service_operations* service_ops;
};

__BEGIN_DECLS

__END_DECLS

#endif