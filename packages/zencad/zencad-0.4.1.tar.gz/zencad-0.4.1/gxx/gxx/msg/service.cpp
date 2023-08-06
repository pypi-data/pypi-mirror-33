#include <gxx/msg/service.h>
#include <gxx/datastruct/dlist_head.h>

static g0id_t service_id_counter = 0;
static g0id_t message_id_counter = 0;

#ifndef GENOS_SERVICE_TABLE_SIZE
#define G0_SERVICE_TABLE_SIZE 20
#endif

struct hlist_head service_htable [G0_SERVICE_TABLE_SIZE];

g0id_t g0_getid_service() { 
	return ++service_id_counter; 
}

g0id_t g0_getid_message() { 
	return ++message_id_counter; 
}

gxx::msg::id_t gxx::msg::getid_service();
gxx::msg::id_t gxx::msg::getid_message();

gxx::msg::id_t gxx::msg::init_service(struct gxx::msg::service* srv);
gxx::msg::id_t gxx::msg::init_message(struct gxx::msg::message* srv);


