
class RawPaginator(object):
    """
    Generator to paginate over list results and return JSON data
    """

    listkey = 'list'
    itemkey = 'item'

    def __init__(self, client, *request_args, **request_kwargs):
        self.client = client
        self.data = {}
        self.request_args = request_args
        self.request_kwargs = request_kwargs
        self.current_offset = 0
        self.max = request_kwargs.get('max', 30)

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.data.get(self.itemkey, [])) < 1:
            if self.itemkey in self.data and \
                    self.current_offset >= self.data['end']:
                raise StopIteration
            self._fetch_next()
        return self.data[self.itemkey].pop(0)

    def _fetch_next(self):
        self.request_kwargs['offset'] = self.current_offset
        self.data = self.client.run_request(
            *self.request_args, **self.request_kwargs)[self.listkey]
        self.current_offset += self.max


class RawNutrientReportPaginator(RawPaginator):
    listkey = 'report'
    itemkey = 'foods'


class ModelPaginator(object):
    """
    Generator to paginate over list results and get custom models
    """

    def __init__(self, model, raw):
        assert isinstance(raw, RawPaginator)
        self.model = model
        self.raw = raw

    def __iter__(self):
        return self

    def __next__(self):
        return self.model.from_response_data(next(self.raw))
