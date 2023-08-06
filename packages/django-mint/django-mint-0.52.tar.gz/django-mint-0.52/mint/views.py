def with_id(request, coordinator, ctx, idx, action=None):
    api = coordinator(request, ctx, idx=idx, action=action)
    return api.run()


def without_id(request, coordinator, ctx, action=None):
    api = coordinator(request, ctx, action=action)
    return api.run()