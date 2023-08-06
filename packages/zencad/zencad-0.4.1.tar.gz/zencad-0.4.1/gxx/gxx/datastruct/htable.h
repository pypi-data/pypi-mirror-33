#ifndef DATASTRUCT_LINHTABLE_H
#define DATASTRUCT_LINHTABLE_H

#include <gxx/datastruct/hlist_head.h>

__BEGIN_DECLS

static inline void htable_init(struct hlist_head* harray, size_t size) { 												\
	for(struct hlist_head *it = harray, *eit = harray + size; it != eit; ++it) {
		hlist_head_init(it);
	}
}

__END_DECLS

#endif