#ifndef GXX_MSG_SERVICE_H
#define GXX_MSG_SERVICE_H

#include <gxx/datastruct/dlist_head.h>

namespace gxx { 
	namespace msg {
		using id_t = uint16_t;

		struct message {
			struct dlist_head qlnk; //к листу входящих сервиса.
			id_t qid;				//ид сообщения. хэш таблицы сообщений.
			id_t sid; 				//ид отправителя.
			id_t rid;				//ид получателя.
		
			void* data;
			size_t size;
		
			union {
				struct {
//					uint8_t sended : 1;
//					uint8_t recved : 1;
					uint8_t repled : 1;
					uint8_t noreply : 1;
					//uint8_t nodeallocate : 1;
				};
				uint8_t stsbyte;
			};

		};

		struct service {
			struct hlist_node hlnk;		//к таблице сервисов.
			g0id_t id;					//ид. хэш таблицы сервисов.
			virtual void on_input(message* msg) = 0;
		};

		id_t getid_service();
		id_t getid_message();

		id_t init_service(struct service* srv);
		id_t init_message(struct message* srv);


	} 
}

#endif