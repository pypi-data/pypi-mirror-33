import abjad


class QuantizationJob(abjad.AbjadObject):
    r'''Quantization job.

    Copiable, picklable class for generating all ``QGrids`` which are valid
    under a given ``SearchTree`` for a sequence of ``QEventProxies``.

    ..  container:: example

        >>> q_event_a = abjadext.nauert.PitchedQEvent(250, [0, 1])
        >>> q_event_b = abjadext.nauert.SilentQEvent(500)
        >>> q_event_c = abjadext.nauert.PitchedQEvent(750, [3, 7])
        >>> proxy_a = abjadext.nauert.QEventProxy(q_event_a, 0.25)
        >>> proxy_b = abjadext.nauert.QEventProxy(q_event_b, 0.5)
        >>> proxy_c = abjadext.nauert.QEventProxy(q_event_c, 0.75)

        >>> definition = {2: {2: None}, 3: None, 5: None}
        >>> search_tree = abjadext.nauert.UnweightedSearchTree(definition)

        >>> job = abjadext.nauert.QuantizationJob(
        ...     1, search_tree, [proxy_a, proxy_b, proxy_c])

    ..  container:: example

        ``QuantizationJob`` generates ``QGrids`` when called, and stores those
        ``QGrids`` on its ``q_grids`` attribute, allowing them to be recalled
        later, even if pickled:

        >>> job()
        >>> for q_grid in job.q_grids:
        ...     print(q_grid.rtm_format)
        1
        (1 (1 1 1 1 1))
        (1 (1 1 1))
        (1 (1 1))
        (1 ((1 (1 1)) (1 (1 1))))

    ``QuantizationJob`` is intended to be useful in multiprocessing-enabled
    environments.
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_job_id',
        '_q_event_proxies',
        '_q_grids',
        '_search_tree',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        job_id=1,
        search_tree=None,
        q_event_proxies=None,
        q_grids=None,
        ):
        import abjadext.nauert
        search_tree = search_tree or abjadext.nauert.UnweightedSearchTree()
        q_event_proxies = q_event_proxies or []
        assert isinstance(search_tree, abjadext.nauert.SearchTree)
        assert all(
            isinstance(x, abjadext.nauert.QEventProxy)
            for x in q_event_proxies
            )
        self._job_id = job_id
        self._search_tree = search_tree
        self._q_event_proxies = tuple(q_event_proxies)
        if q_grids is None:
            self._q_grids = ()
        else:
            assert all(
                isinstance(x, abjadext.nauert.QGrid)
                for x in q_grids
                )
            self._q_grids = tuple(q_grids)

    ### SPECIAL METHODS ###

    def __call__(self):
        r'''Calls quantization job.

        Returns none.
        '''
        import abjadext.nauert
        #print('XXX')
        #print(format(self.q_event_proxies[0]))

        q_grid = abjadext.nauert.QGrid()
        q_grid.fit_q_events(self.q_event_proxies)

        #print(format(q_grid))

        old_q_grids = []
        new_q_grids = [q_grid]

        while new_q_grids:
            q_grid = new_q_grids.pop()
            search_results = self.search_tree(q_grid)
            #print q_grid.rtm_format
            #for x in search_results:
            #    print '\t', x.rtm_format
            new_q_grids.extend(search_results)
            old_q_grids.append(q_grid)

        #for q_grid in old_q_grids:
        #    print('\t', q_grid)
        #print()

        self._q_grids = tuple(old_q_grids)

    def __eq__(self, argument):
        r'''Is true when `argument` is a quantization job with job ID, search tree,
        q-event proxies and q-grids equal to those of this quantization job.
        Otherwise false.

        Returns true or false.
        '''
        if type(self) == type(argument):
            if self.job_id == argument.job_id:
                if self.search_tree == argument.search_tree:
                    if self.q_event_proxies == argument.q_event_proxies:
                        if self.q_grids == argument.q_grids:
                            return True
        return False

    def __hash__(self):
        r'''Hashes quantization job.

        Required to be explicitly redefined on Python 3 if __eq__ changes.

        Returns integer.
        '''
        return super(QuantizationJob, self).__hash__()

    ### PUBLIC PROPERTIES ###

    @property
    def job_id(self):
        r'''The job id of the ``QuantizationJob``.

        Only meaningful when the job is processed via multiprocessing,
        as the job id is necessary to reconstruct the order of jobs.

        Returns int.
        '''
        return self._job_id

    @property
    def q_event_proxies(self):
        r'''The ``QEventProxies`` the ``QuantizationJob`` was instantiated
        with.

        >>> q_event_a = abjadext.nauert.PitchedQEvent(250, [0, 1])
        >>> q_event_b = abjadext.nauert.SilentQEvent(500)
        >>> q_event_c = abjadext.nauert.PitchedQEvent(750, [3, 7])
        >>> proxy_a = abjadext.nauert.QEventProxy(q_event_a, 0.25)
        >>> proxy_b = abjadext.nauert.QEventProxy(q_event_b, 0.5)
        >>> proxy_c = abjadext.nauert.QEventProxy(q_event_c, 0.75)

        >>> definition = {2: {2: None}, 3: None, 5: None}
        >>> search_tree = abjadext.nauert.UnweightedSearchTree(definition)

        >>> job = abjadext.nauert.QuantizationJob(
        ...     1, search_tree, [proxy_a, proxy_b, proxy_c])
        >>> job()

        >>> for q_event_proxy in job.q_event_proxies:
        ...     print(format(q_event_proxy, 'storage'))
        ...
        abjadext.nauert.QEventProxy(
            abjadext.nauert.PitchedQEvent(
                offset=abjad.Offset(250, 1),
                pitches=(
                    abjad.NamedPitch("c'"),
                    abjad.NamedPitch("cs'"),
                    ),
                ),
            abjad.Offset(1, 4)
            )
        abjadext.nauert.QEventProxy(
            abjadext.nauert.SilentQEvent(
                offset=abjad.Offset(500, 1),
                ),
            abjad.Offset(1, 2)
            )
        abjadext.nauert.QEventProxy(
            abjadext.nauert.PitchedQEvent(
                offset=abjad.Offset(750, 1),
                pitches=(
                    abjad.NamedPitch("ef'"),
                    abjad.NamedPitch("g'"),
                    ),
                ),
            abjad.Offset(3, 4)
            )

        Returns tuple.
        '''
        return self._q_event_proxies

    @property
    def q_grids(self):
        r'''The generated ``QGrids``.

        >>> q_event_a = abjadext.nauert.PitchedQEvent(250, [0, 1])
        >>> q_event_b = abjadext.nauert.SilentQEvent(500)
        >>> q_event_c = abjadext.nauert.PitchedQEvent(750, [3, 7])
        >>> proxy_a = abjadext.nauert.QEventProxy(q_event_a, 0.25)
        >>> proxy_b = abjadext.nauert.QEventProxy(q_event_b, 0.5)
        >>> proxy_c = abjadext.nauert.QEventProxy(q_event_c, 0.75)

        >>> definition = {2: {2: None}, 3: None, 5: None}
        >>> search_tree = abjadext.nauert.UnweightedSearchTree(definition)

        >>> job = abjadext.nauert.QuantizationJob(
        ...     1, search_tree, [proxy_a, proxy_b, proxy_c])
        >>> job()

        >>> for q_grid in job.q_grids:
        ...     print(q_grid.rtm_format)
        1
        (1 (1 1 1 1 1))
        (1 (1 1 1))
        (1 (1 1))
        (1 ((1 (1 1)) (1 (1 1))))

        Returns tuple.
        '''
        return self._q_grids

    @property
    def search_tree(self):
        r'''The search tree the ``QuantizationJob`` was instantiated with.

        Return ``SearchTree`` instance.
        '''
        return self._search_tree
