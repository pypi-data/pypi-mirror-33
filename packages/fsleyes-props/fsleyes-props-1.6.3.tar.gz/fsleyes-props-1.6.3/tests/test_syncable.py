#!/usr/bin/env python
#
# test_syncable.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import pytest

import fsleyes_props as props


def test_basic_usage():
    class Foo(props.SyncableHasProperties):
        myint = props.Int(default=0)

    p = Foo()
    c = Foo(parent=p)

    assert c.isSyncedToParent('myint')
    assert c.anySyncedToParent()
    assert c.allSyncedToParent()
    assert c.canBeSyncedToParent('myint')
    assert c.canBeUnsyncedFromParent('myint')

    assert list(p.getChildren()) == [c]
    assert c.getParent()         ==  p

    assert p.myint == 0
    assert c.myint == 0

    p.myint = 10

    assert p.myint == 10
    assert c.myint == 10

    c.myint = 20

    assert p.myint == 20
    assert c.myint == 20


def test_unsync():
    class Foo(props.SyncableHasProperties):
        myint = props.Int(default=0)

    changeCalled = [False]

    def syncChange(*a):
        changeCalled[0] = True

    p = Foo()
    c = Foo(parent=p)

    p.myint = 10
    assert p.myint == 10
    assert c.myint == 10

    c.addSyncChangeListener('myint', 'syncChange', syncChange)

    c.unsyncFromParent('myint')

    assert changeCalled[0]
    changeCalled[0] = False

    p.myint = 20
    assert p.myint == 20
    assert c.myint == 10

    c.syncToParent('myint')

    assert changeCalled[0]
    assert c.myint == 20

    changeCalled[0] = False
    c.removeSyncChangeListener('myint', 'syncChange')

    p.myint = 30
    assert not changeCalled[0]
    assert p.myint == 30
    assert c.myint == 30


def test_unsync_all():
    class Foo(props.SyncableHasProperties):
        int1 = props.Int(default=0)
        int2 = props.Int(default=0)

    p = Foo()
    c = Foo(parent=p)

    p.int1, p.int2 = 10, 20

    assert (c.int1, c.int2) == (10, 20)

    c.unsyncAllFromParent()

    p.int1, p.int2 = 30, 40

    assert c.int1, c.int2 == (10, 20)

    p.int1, p.int2 = 50, 60

    c.syncAllToParent()
    assert (c.int1, c.int2) == (50, 60)



def test_bindingDirection():

    class Foo(props.SyncableHasProperties):
        myint = props.Int(default=0)

    p = Foo()
    c = Foo(parent=p, direction=False)
    assert not c.getBindingDirection('myint')

    p.myint = 10

    c.unsyncFromParent('myint')
    p.myint = 20
    c.myint = 40

    assert p.myint == 20
    assert c.myint == 40

    c.syncToParent('myint')

    assert p.myint == 40
    assert c.myint == 40

    c.unsyncFromParent('myint')
    c.setBindingDirection(True, 'myint')

    p.myint = 75

    c.syncToParent('myint')
    assert p.myint == 75
    assert c.myint == 75


def test_detach():
    class Foo(props.SyncableHasProperties):
        myint = props.Int(default=0)

    p = Foo()
    c = Foo(parent=p)

    p.myint = 25
    assert c.myint == 25

    c.detachFromParent('myint')

    p.myint = 75
    assert c.myint == 25

    c = Foo(parent=p)

    p.myint = 15
    assert c.myint == 15

    c.detachAllFromParent()

    p.myint = 23
    assert c.myint == 15



def test_syncabe_list_link1():  _test_syncabe_list_link(1)
def test_syncabe_list_link2():  _test_syncabe_list_link(2)
def test_syncabe_list_link3():  _test_syncabe_list_link(3)
def test_syncabe_list_link4():  _test_syncabe_list_link(4)
def test_syncabe_list_link5():  _test_syncabe_list_link(5)
def test_syncabe_list_link6():  _test_syncabe_list_link(6)
def test_syncabe_list_link7():  _test_syncabe_list_link(7)
def test_syncabe_list_link8():  _test_syncabe_list_link(8)
def test_syncabe_list_link9():  _test_syncabe_list_link(9)
def test_syncabe_list_link10(): _test_syncabe_list_link(10)

# List properties whcih are synced together, and also
# where, within each instance, individual list items
# are bound across properties
def _test_syncabe_list_link(nchildren):
    class Thing(props.SyncableHasProperties):
        crange = props.Bounds(ndims=1, clamped=False)
        drange = props.Bounds(ndims=1, clamped=False)
        linklo = props.Boolean(default=True)

        def __init__(self, *args, **kwargs):
            props.SyncableHasProperties.__init__(self, *args, **kwargs)
            parent = self.getParent()

            if parent is not None:
                self.addListener('linklo',
                                 str(id(self)),
                                 self.__linkloChanged)
                if self.linklo:  self.__linkloChanged()

        def __linkloChanged(self, *a):
            self.__updateLink(self.linklo, 0)

        def __updateLink(self, val, idx):

            drangePV = self.drange.getPropertyValueList()[idx]
            crangePV = self.crange.getPropertyValueList()[idx]

            if props.propValsAreBound(drangePV, crangePV) == val:
                return

            props.bindPropVals(drangePV,
                               crangePV,
                               bindval=True,
                               bindatt=False,
                               unbind=not val)

            if val:
                crangePV.set(drangePV.get())

    parent   = Thing()
    children = [Thing(parent=parent) for i in range(nchildren)]

    parent.crange = [10, 20]
    parent.drange = [5,  10]

    for i in [parent] + children:
        assert i.crange == [5, 20]
        assert i.drange == [5, 10]


def test_syncable_class_hierarchy():

    class Boo(props.SyncableHasProperties):
        mybool = props.Boolean()

    class Foo(Boo):
        myint = props.Int()

    bp = Boo()
    bc = Boo(parent=bp)

    bp.mybool = False
    assert(not bc.mybool)
    bp.mybool = True
    assert(bc.mybool)
    bc.mybool = False
    assert(not bp.mybool)
    bc.mybool = True
    assert(bp.mybool)

    fp = Foo()
    fc = Foo(parent=fp)

    fp.mybool = False
    assert(not fc.mybool)
    fp.mybool = True
    assert(fc.mybool)
    fc.mybool = False
    assert(not fp.mybool)
    fc.mybool = True
    assert(fp.mybool)


def test_nobind_nounbind():
    class Foo(props.SyncableHasProperties):
        int1 = props.Int()
        int2 = props.Int()
        int3 = props.Int()

    p = Foo(nobind=['int1'], nounbind=['int2'])
    c = Foo(nobind=['int1'], nounbind=['int2'], parent=p)

    assert not c.canBeSyncedToParent('int1')
    assert     c.canBeSyncedToParent('int2')
    assert     c.canBeSyncedToParent('int3')
    assert     c.canBeUnsyncedFromParent('int1')
    assert not c.canBeUnsyncedFromParent('int2')
    assert     c.canBeUnsyncedFromParent('int3')
    assert not c.isSyncedToParent('int1')
    assert     c.isSyncedToParent('int2')
    assert     c.isSyncedToParent('int3')
    assert     c.anySyncedToParent()
    assert not c.allSyncedToParent()

    p.int1 = 123
    c.int1 = 456
    assert (p.int1, c.int1) == (123, 456)

    p.int2 = 123
    c.int2 = 456
    assert (p.int2, c.int2) == (456, 456)

    p.int3 = 123
    c.int3 = 456
    assert (p.int3, c.int3) == (456, 456)

    with pytest.raises(props.SyncError):
        c.syncToParent('int1')

    with pytest.raises(props.SyncError):
        c.unsyncFromParent('int2')

    c.detachAllFromParent()

    c.int1, c.int2, c.int3 = 10, 20, 30
    p.int1, p.int2, p.int3 = 40, 50, 60

    assert (c.int1, c.int2, c.int3) == (10, 20, 30)
    assert (p.int1, p.int2, p.int3) == (40, 50, 60)
