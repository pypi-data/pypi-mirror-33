from ctypes import *


class DumpiHeader(Structure):
    _fields_ = [
        ("version", c_byte*3),
        ("starttime", c_ulonglong),
        ("hostname", c_char_p),
        ("username", c_char_p),
        ("meshdim", c_int),
        ("meshcrd", POINTER(c_int)),
        ("meshsize", POINTER(c_int)),
    ]

class DumpiFooter(Structure):
    _fields_ = [
        ("call_count", c_int*291),
        ("ignored_count", c_int*291),
    ]

class DumpiKeyvalEntry(Structure):
    pass

# need to separate the fields here, to allow incomplete type
DumpiKeyvalEntry._fields_ = [
    ("key", c_char_p),
    ("val", c_char_p),
    ("next", POINTER(DumpiKeyvalEntry)),
]

class DumpiKeyvalRecord(Structure):
    _fields_ = [
        ("count", c_int),
        ("head", POINTER(DumpiKeyvalEntry)),
        ("tail", POINTER(DumpiKeyvalEntry)),
    ]

class DumpiSizeof(Structure):
    _fields_ = [
        ("count", c_short),
        ("size", POINTER(c_int)),
    ]

class DumpiClock(Structure):
    _fields_ = [
        ("sec", c_int),
        ("nsec", c_int),
    ]

    def __str__(self):
        return "DumpiClock(sec={0}, nsec={1})]".format(self.sec, self.nsec)

    def to_sec(self):
        return self.sec + self.nsec / 1e9

    def to_ms(self):
        return self.sec * 1000 + self.nsec * 1e-6

    def to_ns(self):
        return int(self.nsec + self.sec * 1e9)

    def __sub__(self, rhs):
        nsec = (self.nsec + self.sec * 1e9) - (rhs.nsec + rhs.sec * 1e9)
        result = DumpiClock(int(nsec / 1e9), int(nsec % 1e9)) 
        if nsec < 0:
            result.nsec = abs(result.nsec) \
                if result.sec != 0 else -abs(result.nsec)
        return result

    def __add__(self, rhs):
        nsec = (self.nsec + self.sec * 1e9) + (rhs.nsec + rhs.sec * 1e9)
        result = DumpiClock(int(nsec / 1e9), int(nsec % 1e9)) 
        if nsec < 0:
            result.nsec = abs(result.nsec) \
                if result.sec != 0 else -abs(result.nsec)
        return result

class DumpiTime(Structure):
    _fields_ = [
        ("start", DumpiClock),
        ("stop", DumpiClock),
    ]

class DumpiPerfInfo(Structure):
    _fields_ = [
        ("count", c_int),
        ("counter_tag", (c_char * 128) * 80),
        ("invalue", c_longlong * 128),
        ("outvalue", c_longlong * 128),
    ]

class File(Structure):
    _fields_ = [
    ]

class DumpiMemoryBuffer(Structure):
    _fields_ = [
        ("length", c_size_t),
        ("pos", c_size_t),
        ("buffer", POINTER(c_ubyte)),
    ]

class DumpiProfile(Structure):
    _fields_ = [
        ("file", POINTER(File)),
        ("cpu_time_offset", c_int),
        ("wall_time_offset", c_int),
        ("header", c_long),
        ("body", c_long),
        ("footer", c_long),
        ("keyval", c_long),
        ("perflbl", c_long),
        ("addrlbl", c_long),
        ("sizelbl", c_long),
        ("version", c_char*3),
        ("membuf", POINTER(DumpiMemoryBuffer)),
        ("target_membuf_size", c_size_t),
    ]

class DumpiStatus(Structure):
    _fields_ = [
        ("bytes", c_int),
        ("source", c_int),
        ("tag", c_int),
        ("cancelled", c_byte),
        ("error", c_byte),
    ]

class DumpiFuncCall(Structure):
    _fields_ = [
        ("fn", c_longlong),
    ]

class DumpiSend(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("dest", c_int),
        ("tag", c_int),
        ("comm", c_short),
    ]

class DumpiRecv(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("source", c_int),
        ("tag", c_int),
        ("comm", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiGetCount(Structure):
    _fields_ = [
        ("status", POINTER(DumpiStatus)),
        ("datatype", c_short),
        ("count", c_int),
    ]

class DumpiBSend(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("dest", c_int),
        ("tag", c_int),
        ("comm", c_short),
    ]

class DumpiSSend(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("dest", c_int),
        ("tag", c_int),
        ("comm", c_short),
    ]

class DumpiRSend(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("dest", c_int),
        ("tag", c_int),
        ("comm", c_short),
    ]

class DumpiBufferAttach(Structure):
    _fields_ = [
        ("size", c_int),
    ]

class DumpiBufferDetach(Structure):
    _fields_ = [
        ("size", c_int),
    ]

class DumpiISend(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("dest", c_int),
        ("tag", c_int),
        ("comm", c_short),
        ("request", c_int),
    ]

class DumpiIbSend(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("dest", c_int),
        ("tag", c_int),
        ("comm", c_short),
        ("request", c_int),
    ]

class DumpiIsSend(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("dest", c_int),
        ("tag", c_int),
        ("comm", c_short),
        ("request", c_int),
    ]

class DumpiIrSend(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("dest", c_int),
        ("tag", c_int),
        ("comm", c_short),
        ("request", c_int),
    ]

class DumpiIRecv(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("source", c_int),
        ("tag", c_int),
        ("comm", c_short),
        ("request", c_int),
    ]

class DumpiWait(Structure):
    _fields_ = [
        ("request", c_int),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiTest(Structure):
    _fields_ = [
        ("request", c_int),
        ("flag", c_int),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiRequestFree(Structure):
    _fields_ = [
        ("request", c_int),
    ]

class DumpiWaitAny(Structure):
    _fields_ = [
        ("count", c_int),
        ("requests", POINTER(c_int)),
        ("index", c_int),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiTestAny(Structure):
    _fields_ = [
        ("count", c_int),
        ("requests", POINTER(c_int)),
        ("index", c_int),
        ("flag", c_int),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiWaitAll(Structure):
    _fields_ = [
        ("count", c_int),
        ("requests", POINTER(c_int)),
        ("statuses", POINTER(DumpiStatus)),
    ]

class DumpiTestAll(Structure):
    _fields_ = [
        ("count", c_int),
        ("requests", POINTER(c_int)),
        ("flag", c_int),
        ("statuses", POINTER(DumpiStatus)),
    ]

class DumpiWaitSome(Structure):
    _fields_ = [
        ("count", c_int),
        ("requests", POINTER(c_int)),
        ("outcount", c_int),
        ("indices", POINTER(c_int)),
        ("statuses", POINTER(DumpiStatus)),
    ]

class DumpiTestSome(Structure):
    _fields_ = [
        ("count", c_int),
        ("requests", POINTER(c_int)),
        ("outcount", c_int),
        ("indices", POINTER(c_int)),
        ("statuses", POINTER(DumpiStatus)),
    ]

class DumpiIProbe(Structure):
    _fields_ = [
        ("source", c_int),
        ("tag", c_int),
        ("comm", c_short),
        ("flag", c_int),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiProbe(Structure):
    _fields_ = [
        ("source", c_int),
        ("tag", c_int),
        ("comm", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiCancel(Structure):
    _fields_ = [
        ("request", c_int),
    ]

class DumpiTestCancelled(Structure):
    _fields_ = [
        ("status", POINTER(DumpiStatus)),
        ("cancelled", c_int),
    ]

class DumpiSendInit(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("dest", c_int),
        ("tag", c_int),
        ("comm", c_short),
        ("request", c_int),
    ]

class DumpiBsendInit(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("dest", c_int),
        ("tag", c_int),
        ("comm", c_short),
        ("request", c_int),
    ]

class DumpiSsendInit(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("dest", c_int),
        ("tag", c_int),
        ("comm", c_short),
        ("request", c_int),
    ]

class DumpiRsendInit(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("dest", c_int),
        ("tag", c_int),
        ("comm", c_short),
        ("request", c_int),
    ]

class DumpiRecvInit(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("source", c_int),
        ("tag", c_int),
        ("comm", c_short),
        ("request", c_int),
    ]

class DumpiStart(Structure):
    _fields_ = [
        ("request", c_int),
    ]

class DumpiStartall(Structure):
    _fields_ = [
        ("count", c_int),
        ("requests", POINTER(c_int)),
    ]

class DumpiSendrecv(Structure):
    _fields_ = [
        ("sendcount", c_int),
        ("sendtype", c_short),
        ("dest", c_int),
        ("sendtag", c_int),
        ("recvcount", c_int),
        ("recvtype", c_short),
        ("source", c_int),
        ("recvtag", c_int),
        ("comm", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiSendrecvReplace(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("dest", c_int),
        ("sendtag", c_int),
        ("source", c_int),
        ("recvtag", c_int),
        ("comm", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiTypeContiguous(Structure):
    _fields_ = [
        ("count", c_int),
        ("oldtype", c_short),
        ("newtype", c_short),
    ]

class DumpiTypeVector(Structure):
    _fields_ = [
        ("count", c_int),
        ("blocklength", c_int),
        ("stride", c_int),
        ("oldtype", c_short),
        ("newtype", c_short),
    ]

class DumpiTypeHvector(Structure):
    _fields_ = [
        ("count", c_int),
        ("blocklength", c_int),
        ("stride", c_int),
        ("oldtype", c_short),
        ("newtype", c_short),
    ]

class DumpiTypeIndexed(Structure):
    _fields_ = [
        ("count", c_int),
        ("lengths", POINTER(c_int)),
        ("indices", POINTER(c_int)),
        ("oldtype", c_short),
        ("newtype", c_short),
    ]

class DumpiTypeHindexed(Structure):
    _fields_ = [
        ("count", c_int),
        ("lengths", POINTER(c_int)),
        ("indices", POINTER(c_int)),
        ("oldtype", c_short),
        ("newtype", c_short),
    ]

class DumpiTypeStruct(Structure):
    _fields_ = [
        ("count", c_int),
        ("lengths", POINTER(c_int)),
        ("indices", POINTER(c_int)),
        ("oldtypes", POINTER(c_short)),
        ("newtype", c_short),
    ]

class DumpiAddress(Structure):
    _fields_ = [
        ("address", c_int),
    ]

class DumpiTypeExtent(Structure):
    _fields_ = [
        ("datatype", c_short),
        ("extent", c_int),
    ]

class DumpiTypeSize(Structure):
    _fields_ = [
        ("datatype", c_short),
        ("size", c_int),
    ]

class DumpiTypeLb(Structure):
    _fields_ = [
        ("datatype", c_short),
        ("lb", c_int),
    ]

class DumpiTypeUb(Structure):
    _fields_ = [
        ("datatype", c_short),
        ("ub", c_int),
    ]

class DumpiTypeCommit(Structure):
    _fields_ = [
        ("datatype", c_short),
    ]

class DumpiTypeFree(Structure):
    _fields_ = [
        ("datatype", c_short),
    ]

class DumpiGetElements(Structure):
    _fields_ = [
        ("status", POINTER(DumpiStatus)),
        ("datatype", c_short),
        ("elements", c_int),
    ]

class DumpiPack(Structure):
    _fields_ = [
        ("incount", c_int),
        ("datatype", c_short),
        ("outcount", c_int),
        ("pos_in", c_int),
        ("pos_out", c_int),
        ("comm", c_short),
    ]

class DumpiUnpack(Structure):
    _fields_ = [
        ("incount", c_int),
        ("pos_in", c_int),
        ("pos_out", c_int),
        ("outcount", c_int),
        ("datatype", c_short),
        ("comm", c_short),
    ]

class DumpiPackSize(Structure):
    _fields_ = [
        ("incount", c_int),
        ("datatype", c_short),
        ("comm", c_short),
        ("size", c_int),
    ]

class DumpiBarrier(Structure):
    _fields_ = [
        ("comm", c_short),
    ]

class DumpiBcast(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("root", c_int),
        ("comm", c_short),
    ]

class DumpiGather(Structure):
    _fields_ = [
        ("commrank", c_int),
        ("sendcount", c_int),
        ("sendtype", c_short),
        ("recvcount", c_int),
        ("recvtype", c_short),
        ("root", c_int),
        ("comm", c_short),
    ]

class DumpiGatherv(Structure):
    _fields_ = [
        ("commrank", c_int),
        ("commsize", c_int),
        ("sendcount", c_int),
        ("sendtype", c_short),
        ("recvcounts", POINTER(c_int)),
        ("displs", POINTER(c_int)),
        ("recvtype", c_short),
        ("root", c_int),
        ("comm", c_short),
    ]

class DumpiScatter(Structure):
    _fields_ = [
        ("commrank", c_int),
        ("sendcount", c_int),
        ("sendtype", c_short),
        ("recvcount", c_int),
        ("recvtype", c_short),
        ("root", c_int),
        ("comm", c_short),
    ]

class DumpiScatterv(Structure):
    _fields_ = [
        ("commrank", c_int),
        ("commsize", c_int),
        ("sendcounts", POINTER(c_int)),
        ("displs", POINTER(c_int)),
        ("sendtype", c_short),
        ("recvcount", c_int),
        ("recvtype", c_short),
        ("root", c_int),
        ("comm", c_short),
    ]

class DumpiAllgather(Structure):
    _fields_ = [
        ("sendcount", c_int),
        ("sendtype", c_short),
        ("recvcount", c_int),
        ("recvtype", c_short),
        ("comm", c_short),
    ]

class DumpiAllgatherv(Structure):
    _fields_ = [
        ("commsize", c_int),
        ("sendcount", c_int),
        ("sendtype", c_short),
        ("recvcounts", POINTER(c_int)),
        ("displs", POINTER(c_int)),
        ("recvtype", c_short),
        ("comm", c_short),
    ]

class DumpiAlltoall(Structure):
    _fields_ = [
        ("sendcount", c_int),
        ("sendtype", c_short),
        ("recvcount", c_int),
        ("recvtype", c_short),
        ("comm", c_short),
    ]

class DumpiAlltoallv(Structure):
    _fields_ = [
        ("commsize", c_int),
        ("sendcounts", POINTER(c_int)),
        ("senddispls", POINTER(c_int)),
        ("sendtype", c_short),
        ("recvcounts", POINTER(c_int)),
        ("recvdispls", POINTER(c_int)),
        ("recvtype", c_short),
        ("comm", c_short),
    ]

class DumpiReduce(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("op", c_short),
        ("root", c_int),
        ("comm", c_short),
    ]

class DumpiOpCreate(Structure):
    _fields_ = [
        ("commute", c_int),
        ("op", c_short),
    ]

class DumpiOpFree(Structure):
    _fields_ = [
        ("op", c_short),
    ]

class DumpiAllreduce(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("op", c_short),
        ("comm", c_short),
    ]

class DumpiReduceScatter(Structure):
    _fields_ = [
        ("commsize", c_int),
        ("recvcounts", POINTER(c_int)),
        ("datatype", c_short),
        ("op", c_short),
        ("comm", c_short),
    ]

class DumpiScan(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("op", c_short),
        ("comm", c_short),
    ]

class DumpiGroupSize(Structure):
    _fields_ = [
        ("group", c_short),
        ("size", c_int),
    ]

class DumpiGroupRank(Structure):
    _fields_ = [
        ("group", c_short),
        ("rank", c_int),
    ]

class DumpiGroupTranslateRanks(Structure):
    _fields_ = [
        ("group1", c_short),
        ("count", c_int),
        ("ranks1", POINTER(c_int)),
        ("group2", c_short),
        ("ranks2", POINTER(c_int)),
    ]

class DumpiGroupCompare(Structure):
    _fields_ = [
        ("group1", c_short),
        ("group2", c_short),
        ("result", c_byte),
    ]

class DumpiCommGroup(Structure):
    _fields_ = [
        ("comm", c_short),
        ("group", c_short),
    ]

class DumpiGroupUnion(Structure):
    _fields_ = [
        ("group1", c_short),
        ("group2", c_short),
        ("newgroup", c_short),
    ]

class DumpiGroupIntersection(Structure):
    _fields_ = [
        ("group1", c_short),
        ("group2", c_short),
        ("newgroup", c_short),
    ]

class DumpiGroupDifference(Structure):
    _fields_ = [
        ("group1", c_short),
        ("group2", c_short),
        ("newgroup", c_short),
    ]

class DumpiGroupIncl(Structure):
    _fields_ = [
        ("group", c_short),
        ("count", c_int),
        ("ranks", POINTER(c_int)),
        ("newgroup", c_short),
    ]

class DumpiGroupExcl(Structure):
    _fields_ = [
        ("group", c_short),
        ("count", c_int),
        ("ranks", POINTER(c_int)),
        ("newgroup", c_short),
    ]

class DumpiGroupRangeIncl(Structure):
    _fields_ = [
        ("group", c_short),
        ("count", c_int),
        ("ranges", POINTER(POINTER(c_int))),
        ("newgroup", c_short),
    ]

class DumpiGroupRangeExcl(Structure):
    _fields_ = [
        ("group", c_short),
        ("count", c_int),
        ("ranges", POINTER(POINTER(c_int))),
        ("newgroup", c_short),
    ]

class DumpiGroupFree(Structure):
    _fields_ = [
        ("group", c_short),
    ]

class DumpiCommSize(Structure):
    _fields_ = [
        ("comm", c_short),
        ("size", c_int),
    ]

class DumpiCommRank(Structure):
    _fields_ = [
        ("comm", c_short),
        ("rank", c_int),
    ]

class DumpiCommCompare(Structure):
    _fields_ = [
        ("comm1", c_short),
        ("comm2", c_short),
        ("result", c_byte),
    ]

class DumpiCommDup(Structure):
    _fields_ = [
        ("oldcomm", c_short),
        ("newcomm", c_short),
    ]

class DumpiCommCreate(Structure):
    _fields_ = [
        ("oldcomm", c_short),
        ("group", c_short),
        ("newcomm", c_short),
    ]

class DumpiCommSplit(Structure):
    _fields_ = [
        ("oldcomm", c_short),
        ("color", c_int),
        ("key", c_int),
        ("newcomm", c_short),
    ]

class DumpiCommFree(Structure):
    _fields_ = [
        ("comm", c_short),
    ]

class DumpiCommTestInter(Structure):
    _fields_ = [
        ("comm", c_short),
        ("inter", c_int),
    ]

class DumpiCommRemoteSize(Structure):
    _fields_ = [
        ("comm", c_short),
        ("size", c_int),
    ]

class DumpiCommRemoteGroup(Structure):
    _fields_ = [
        ("comm", c_short),
        ("group", c_short),
    ]

class DumpiIntercommCreate(Structure):
    _fields_ = [
        ("localcomm", c_short),
        ("localleader", c_int),
        ("remotecomm", c_short),
        ("remoteleader", c_int),
        ("tag", c_int),
        ("newcomm", c_short),
    ]

class DumpiIntercommMerge(Structure):
    _fields_ = [
        ("comm", c_short),
        ("hight", c_int),
        ("newcomm", c_short),
    ]

class DumpiKeyvalCreate(Structure):
    _fields_ = [
        ("key", c_short),
    ]

class DumpiKeyvalFree(Structure):
    _fields_ = [
        ("key", c_short),
    ]

class DumpiAttrPut(Structure):
    _fields_ = [
        ("comm", c_short),
        ("key", c_int),
    ]

class DumpiAttrGet(Structure):
    _fields_ = [
        ("comm", c_short),
        ("key", c_int),
        ("flag", c_int),
    ]

class DumpiAttrDelete(Structure):
    _fields_ = [
        ("comm", c_short),
        ("key", c_int),
    ]

class DumpiTopoTest(Structure):
    _fields_ = [
        ("comm", c_short),
        ("topology", c_short),
    ]

class DumpiCartCreate(Structure):
    _fields_ = [
        ("oldcomm", c_short),
        ("ndim", c_int),
        ("dims", POINTER(c_int)),
        ("periods", POINTER(c_int)),
        ("reorder", c_int),
        ("newcomm", c_short),
    ]

class DumpiDimsCreate(Structure):
    _fields_ = [
        ("nodes", c_int),
        ("ndim", c_int),
        ("pos_in", POINTER(c_int)),
        ("pos_out", POINTER(c_int)),
    ]

class DumpiGraphCreate(Structure):
    _fields_ = [
        ("numedges", c_int),
        ("oldcomm", c_short),
        ("nodes", c_int),
        ("index", POINTER(c_int)),
        ("edges", POINTER(c_int)),
        ("reoder", c_int),
        ("newcomm", c_short),
    ]

class DumpiGraphdimsGet(Structure):
    _fields_ = [
        ("comm", c_short),
        ("nodes", c_int),
        ("edges", c_int),
    ]

class DumpiGraphGet(Structure):
    _fields_ = [
        ("totedges", c_int),
        ("totnodes", c_int),
        ("comm", c_short),
        ("maxindex", c_int),
        ("maxedges", c_int),
        ("index", POINTER(c_int)),
        ("edges", POINTER(c_int)),
    ]

class DumpiCartdimGet(Structure):
    _fields_ = [
        ("comm", c_short),
        ("ndim", c_int),
    ]

class DumpiCartGet(Structure):
    _fields_ = [
        ("ndim", c_int),
        ("comm", c_short),
        ("maxdims", c_int),
        ("dims", POINTER(c_int)),
        ("periods", POINTER(c_int)),
        ("coords", POINTER(c_int)),
    ]

class DumpiCartRank(Structure):
    _fields_ = [
        ("ndim", c_int),
        ("comm", c_short),
        ("coords", POINTER(c_int)),
        ("rank", c_int),
    ]

class DumpiCartCoords(Structure):
    _fields_ = [
        ("ndim", c_int),
        ("comm", c_short),
        ("rank", c_int),
        ("maxdims", c_int),
        ("coords", POINTER(c_int)),
    ]

class DumpiGraphNeighborsCount(Structure):
    _fields_ = [
        ("comm", c_short),
        ("rank", c_int),
        ("nneigh", c_int),
    ]

class DumpiGraphNeighbors(Structure):
    _fields_ = [
        ("nneigh", c_int),
        ("comm", c_short),
        ("rank", c_int),
        ("maxneighbors", c_int),
        ("neighbors", POINTER(c_int)),
    ]

class DumpiCartShift(Structure):
    _fields_ = [
        ("comm", c_short),
        ("direction", c_int),
        ("displ", c_int),
        ("source", c_int),
        ("dest", c_int),
    ]

class DumpiCartSub(Structure):
    _fields_ = [
        ("ndim", c_int),
        ("oldcomm", c_short),
        ("remain_dim", POINTER(c_int)),
        ("newcomm", c_short),
    ]

class DumpiCartMap(Structure):
    _fields_ = [
        ("comm", c_short),
        ("ndim", c_int),
        ("dims", POINTER(c_int)),
        ("period", POINTER(c_int)),
        ("newrank", c_int),
    ]

class DumpiGraphMap(Structure):
    _fields_ = [
        ("numedges", c_int),
        ("comm", c_short),
        ("nodes", c_int),
        ("index", POINTER(c_int)),
        ("edges", POINTER(c_int)),
        ("newrank", c_int),
    ]

class DumpiGetProcessorName(Structure):
    _fields_ = [
        ("name", c_char_p),
        ("resultlen", c_int),
    ]

class DumpiGetVersion(Structure):
    _fields_ = [
        ("version", c_int),
        ("subversion", c_int),
    ]

class DumpiErrhandlerCreate(Structure):
    _fields_ = [
        ("errhandler", c_short),
    ]

class DumpiErrhandlerSet(Structure):
    _fields_ = [
        ("comm", c_short),
        ("errhandler", c_short),
    ]

class DumpiErrhandlerGet(Structure):
    _fields_ = [
        ("comm", c_short),
        ("errhandler", c_short),
    ]

class DumpiErrhandlerFree(Structure):
    _fields_ = [
        ("errhandler", c_short),
    ]

class DumpiErrorString(Structure):
    _fields_ = [
        ("errorcode", c_int),
        ("errorstring", c_char_p),
        ("resultlen", c_int),
    ]

class DumpiErrorClass(Structure):
    _fields_ = [
        ("errorcode", c_int),
        ("errorclass", c_int),
    ]

class DumpiWtime(Structure):
    _fields_ = [
        ("psec", c_ulonglong),
    ]

class DumpiWtick(Structure):
    _fields_ = [
        ("psec", c_ulonglong),
    ]

class DumpiInit(Structure):
    _fields_ = [
        ("argc", c_int),
        ("argv", POINTER(POINTER(c_char))),
    ]

class DumpiFinalize(Structure):
    _fields_ = [
        ("dummy", c_int),
    ]

class DumpiInitialized(Structure):
    _fields_ = [
        ("result", c_int),
    ]

class DumpiAbort(Structure):
    _fields_ = [
        ("comm", c_short),
        ("errorcode", c_int),
    ]

class DumpiClosePort(Structure):
    _fields_ = [
        ("portname", c_char_p),
    ]

class DumpiCommAccept(Structure):
    _fields_ = [
        ("portname", c_char_p),
        ("info", c_short),
        ("root", c_int),
        ("oldcomm", c_short),
        ("newcomm", c_short),
    ]

class DumpiCommConnect(Structure):
    _fields_ = [
        ("portname", c_char_p),
        ("info", c_short),
        ("root", c_int),
        ("oldcomm", c_short),
        ("newcomm", c_short),
    ]

class DumpiCommDisconnect(Structure):
    _fields_ = [
        ("comm", c_short),
    ]

class DumpiCommGetParent(Structure):
    _fields_ = [
        ("parent", c_short),
    ]

class DumpiCommJoin(Structure):
    _fields_ = [
        ("fd", c_int),
        ("comm", c_short),
    ]

class DumpiCommSpawn(Structure):
    _fields_ = [
        ("oldcommrank", c_int),
        ("command", c_char_p),
        ("argv", POINTER(POINTER(c_char))),
        ("maxprocs", c_int),
        ("info", c_short),
        ("root", c_int),
        ("oldcomm", c_short),
        ("newcomm", c_short),
        ("errcodes", c_int),
    ]

class DumpiCommSpawnMultiple(Structure):
    _fields_ = [
        ("totprocs", c_int),
        ("oldcommrank", c_int),
        ("count", c_int),
        ("commands", POINTER(c_char_p)),
        ("argvs", POINTER(POINTER(POINTER(c_char)))),
        ("maxprocs", POINTER(c_int)),
        ("info", POINTER(c_short)),
        ("root", c_int),
        ("oldcomm", c_short),
        ("newcomm", c_short),
        ("errcodes", c_int),
    ]

class DumpiLookupName(Structure):
    _fields_ = [
        ("servicename", c_char_p),
        ("info", c_short),
        ("portname", c_char_p),
    ]

class DumpiOpenPort(Structure):
    _fields_ = [
        ("info", c_short),
        ("portname", c_char_p),
    ]

class DumpiPublishName(Structure):
    _fields_ = [
        ("servicename", c_char_p),
        ("info", c_short),
        ("portname", c_char_p),
    ]

class DumpiUnpublishName(Structure):
    _fields_ = [
        ("servicename", c_char_p),
        ("info", c_short),
        ("portname", c_char_p),
    ]

class DumpiAccumulate(Structure):
    _fields_ = [
        ("origincount", c_int),
        ("origintype", c_short),
        ("targetrank", c_int),
        ("targetdisp", c_int),
        ("targetcount", c_int),
        ("targettype", c_short),
        ("op", c_short),
        ("win", c_short),
    ]

class DumpiGet(Structure):
    _fields_ = [
        ("origincount", c_int),
        ("origintype", c_short),
        ("targetrank", c_int),
        ("targetdisp", c_int),
        ("targetcount", c_int),
        ("targettype", c_short),
        ("win", c_short),
    ]

class DumpiPut(Structure):
    _fields_ = [
        ("origincount", c_int),
        ("origintype", c_short),
        ("targetrank", c_int),
        ("targetdisp", c_int),
        ("targetcount", c_int),
        ("targettype", c_short),
        ("win", c_short),
    ]

class DumpiWinComplete(Structure):
    _fields_ = [
        ("win", c_short),
    ]

class DumpiWinCreate(Structure):
    _fields_ = [
        ("size", c_int),
        ("dispunit", c_int),
        ("info", c_short),
        ("comm", c_short),
        ("win", c_short),
    ]

class DumpiWinFence(Structure):
    _fields_ = [
        ("assertion", c_short),
        ("win", c_short),
    ]

class DumpiWinFree(Structure):
    _fields_ = [
        ("win", c_short),
    ]

class DumpiWinGetGroup(Structure):
    _fields_ = [
        ("win", c_short),
        ("group", c_short),
    ]

class DumpiWinLock(Structure):
    _fields_ = [
        ("locktype", c_short),
        ("winrank", c_int),
        ("assertion", c_short),
        ("win", c_short),
    ]

class DumpiWinPost(Structure):
    _fields_ = [
        ("group", c_short),
        ("assertion", c_short),
        ("win", c_short),
    ]

class DumpiWinStart(Structure):
    _fields_ = [
        ("group", c_short),
        ("assertion", c_short),
        ("win", c_short),
    ]

class DumpiWinTest(Structure):
    _fields_ = [
        ("win", c_short),
        ("flag", c_int),
    ]

class DumpiWinUnlock(Structure):
    _fields_ = [
        ("winrank", c_int),
        ("win", c_short),
    ]

class DumpiWinWait(Structure):
    _fields_ = [
        ("win", c_short),
    ]

class DumpiAlltoallw(Structure):
    _fields_ = [
        ("commsize", c_int),
        ("sendcounts", POINTER(c_int)),
        ("senddispls", POINTER(c_int)),
        ("sendtypes", POINTER(c_short)),
        ("recvcounts", POINTER(c_int)),
        ("recvdispls", POINTER(c_int)),
        ("recvtypes", POINTER(c_short)),
        ("comm", c_short),
    ]

class DumpiExscan(Structure):
    _fields_ = [
        ("count", c_int),
        ("datatype", c_short),
        ("op", c_short),
        ("comm", c_short),
    ]

class DumpiAddErrorClass(Structure):
    _fields_ = [
        ("errorclass", c_int),
    ]

class DumpiAddErrorCode(Structure):
    _fields_ = [
        ("errorclass", c_int),
        ("errorcode", c_int),
    ]

class DumpiAddErrorString(Structure):
    _fields_ = [
        ("errorcode", c_int),
        ("errorstring", c_char_p),
    ]

class DumpiCommCallErrhandler(Structure):
    _fields_ = [
        ("comm", c_short),
        ("errorcode", c_int),
    ]

class DumpiCommCreateKeyval(Structure):
    _fields_ = [
        ("keyval", c_short),
    ]

class DumpiCommDeleteAttr(Structure):
    _fields_ = [
        ("comm", c_short),
        ("keyval", c_short),
    ]

class DumpiCommFreeKeyval(Structure):
    _fields_ = [
        ("keyval", c_short),
    ]

class DumpiCommGetAttr(Structure):
    _fields_ = [
        ("comm", c_short),
        ("keyval", c_short),
        ("flag", c_int),
    ]

class DumpiCommGetName(Structure):
    _fields_ = [
        ("comm", c_short),
        ("name", c_char_p),
        ("resultlen", c_int),
    ]

class DumpiCommSetAttr(Structure):
    _fields_ = [
        ("comm", c_short),
        ("keyval", c_short),
    ]

class DumpiCommSetName(Structure):
    _fields_ = [
        ("comm", c_short),
        ("name", c_char_p),
    ]

class DumpiFileCallErrhandler(Structure):
    _fields_ = [
        ("file", c_short),
        ("errorcode", c_int),
    ]

class DumpiGrequestComplete(Structure):
    _fields_ = [
        ("request", c_int),
    ]

class DumpiGrequestStart(Structure):
    _fields_ = [
        ("request", c_int),
    ]

class DumpiInitThread(Structure):
    _fields_ = [
        ("argc", c_int),
        ("argv", POINTER(POINTER(c_char))),
        ("tl_required", c_short),
        ("tl_provided", c_short),
    ]

class DumpiIsThreadMain(Structure):
    _fields_ = [
        ("flag", c_int),
    ]

class DumpiQueryThread(Structure):
    _fields_ = [
        ("tl_supported", c_short),
    ]

class DumpiStatusSetCancelled(Structure):
    _fields_ = [
        ("status", POINTER(DumpiStatus)),
        ("flag", c_int),
    ]

class DumpiStatusSetElements(Structure):
    _fields_ = [
        ("status", POINTER(DumpiStatus)),
        ("datatype", c_short),
        ("count", c_int),
    ]

class DumpiTypeCreateKeyval(Structure):
    _fields_ = [
        ("keyval", c_short),
    ]

class DumpiTypeDeleteAttr(Structure):
    _fields_ = [
        ("datatype", c_short),
        ("keyval", c_short),
    ]

class DumpiTypeDup(Structure):
    _fields_ = [
        ("oldtype", c_short),
        ("newtype", c_short),
    ]

class DumpiTypeFreeKeyval(Structure):
    _fields_ = [
        ("keyval", c_short),
    ]

class DumpiTypeGetAttr(Structure):
    _fields_ = [
        ("datatype", c_short),
        ("keyval", c_short),
        ("flag", c_int),
    ]

class DumpiTypeGetContents(Structure):
    _fields_ = [
        ("numdatatypes", c_int),
        ("numaddresses", c_int),
        ("numintegers", c_int),
        ("datatype", c_short),
        ("maxintegers", c_int),
        ("maxaddresses", c_int),
        ("maxdatatyeps", c_int),
        ("arrintegers", POINTER(c_int)),
        ("arraddresses", POINTER(c_int)),
        ("arrdatatypes", POINTER(c_short)),
    ]

class DumpiTypeGetEnvelope(Structure):
    _fields_ = [
        ("datatype", c_short),
        ("numintegers", c_int),
        ("numaddresses", c_int),
        ("numdatatypes", c_int),
        ("combiner", c_short),
    ]

class DumpiTypeGetName(Structure):
    _fields_ = [
        ("datatype", c_short),
        ("name", c_char_p),
        ("resultlen", c_int),
    ]

class DumpiTypeSetAttr(Structure):
    _fields_ = [
        ("datatype", c_short),
        ("keyval", c_short),
    ]

class DumpiTypeSetName(Structure):
    _fields_ = [
        ("datatype", c_short),
        ("name", c_char_p),
    ]

class DumpiTypeMatchSize(Structure):
    _fields_ = [
        ("typeclass", c_short),
        ("size", c_int),
        ("datatype", c_short),
    ]

class DumpiWinCallErrhandler(Structure):
    _fields_ = [
        ("win", c_short),
        ("errorcode", c_int),
    ]

class DumpiWinCreateKeyval(Structure):
    _fields_ = [
        ("keyval", c_short),
    ]

class DumpiWinDeleteAttr(Structure):
    _fields_ = [
        ("win", c_short),
        ("keyval", c_short),
    ]

class DumpiWinFreeKeyval(Structure):
    _fields_ = [
        ("keyval", c_short),
    ]

class DumpiWinGetAttr(Structure):
    _fields_ = [
        ("win", c_short),
        ("keyval", c_short),
        ("flag", c_int),
    ]

class DumpiWinGetName(Structure):
    _fields_ = [
        ("win", c_short),
        ("name", c_char_p),
        ("resultlen", c_int),
    ]

class DumpiWinSetAttr(Structure):
    _fields_ = [
        ("win", c_short),
        ("keyval", c_short),
    ]

class DumpiWinSetName(Structure):
    _fields_ = [
        ("win", c_short),
        ("name", c_char_p),
    ]

class DumpiAllocMem(Structure):
    _fields_ = [
        ("size", c_int),
        ("info", c_short),
    ]

class DumpiCommCreateErrhandler(Structure):
    _fields_ = [
        ("errhandler", c_short),
    ]

class DumpiCommGetErrhandler(Structure):
    _fields_ = [
        ("comm", c_short),
        ("errhandler", c_short),
    ]

class DumpiCommSetErrhandler(Structure):
    _fields_ = [
        ("comm", c_short),
        ("errhandler", c_short),
    ]

class DumpiFileCreateErrhandler(Structure):
    _fields_ = [
        ("errhandler", c_short),
    ]

class DumpiFileGetErrhandler(Structure):
    _fields_ = [
        ("file", c_short),
        ("errhandler", c_short),
    ]

class DumpiFileSetErrhandler(Structure):
    _fields_ = [
        ("file", c_short),
        ("errhandler", c_short),
    ]

class DumpiFinalized(Structure):
    _fields_ = [
        ("flag", c_int),
    ]

class DumpiFreeMem(Structure):
    _fields_ = [
        ("dummy", c_int),
    ]

class DumpiGetAddress(Structure):
    _fields_ = [
        ("address", c_int),
    ]

class DumpiInfoCreate(Structure):
    _fields_ = [
        ("info", c_short),
    ]

class DumpiInfoDelete(Structure):
    _fields_ = [
        ("info", c_short),
        ("key", c_char_p),
    ]

class DumpiInfoDup(Structure):
    _fields_ = [
        ("oldinfo", c_short),
        ("newinfo", c_short),
    ]

class DumpiInfoFree(Structure):
    _fields_ = [
        ("info", c_short),
    ]

class DumpiInfoGet(Structure):
    _fields_ = [
        ("info", c_short),
        ("key", c_char_p),
        ("valuelength", c_int),
        ("value", c_char_p),
        ("flag", c_int),
    ]

class DumpiInfoGetNkeys(Structure):
    _fields_ = [
        ("info", c_short),
        ("nkeys", c_int),
    ]

class DumpiInfoGetNthkey(Structure):
    _fields_ = [
        ("info", c_short),
        ("n", c_int),
        ("key", c_char_p),
    ]

class DumpiInfoGetValuelen(Structure):
    _fields_ = [
        ("info", c_short),
        ("key", c_char_p),
        ("valuelen", c_int),
        ("flag", c_int),
    ]

class DumpiInfoSet(Structure):
    _fields_ = [
        ("info", c_short),
        ("key", c_char_p),
        ("value", c_char_p),
    ]

class DumpiPackExternal(Structure):
    _fields_ = [
        ("datarep", POINTER(c_char)),
        ("incount", c_int),
        ("intype", c_short),
        ("outcount", c_int),
        ("pos_in", c_int),
        ("pos_out", c_int),
    ]

class DumpiPackExternalSize(Structure):
    _fields_ = [
        ("datarep", POINTER(c_char)),
        ("incount", c_int),
        ("datatype", c_short),
        ("size", c_int),
    ]

class DumpiRequestGetStatus(Structure):
    _fields_ = [
        ("request", c_int),
        ("flag", c_int),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiTypeCreateDarray(Structure):
    _fields_ = [
        ("size", c_int),
        ("rank", c_int),
        ("ndims", c_int),
        ("gsizes", POINTER(c_int)),
        ("distribs", POINTER(c_short)),
        ("dargs", POINTER(c_int)),
        ("psizes", POINTER(c_int)),
        ("order", c_byte),
        ("oldtype", c_short),
        ("newtype", c_short),
    ]

class DumpiTypeCreateHindexed(Structure):
    _fields_ = [
        ("count", c_int),
        ("blocklengths", POINTER(c_int)),
        ("displacements", POINTER(c_int)),
        ("oldtype", c_short),
        ("newtype", c_short),
    ]

class DumpiTypeCreateHvector(Structure):
    _fields_ = [
        ("count", c_int),
        ("blocklength", c_int),
        ("stride", c_int),
        ("oldtype", c_short),
        ("newtype", c_short),
    ]

class DumpiTypeCreateIndexedBlock(Structure):
    _fields_ = [
        ("count", c_int),
        ("blocklength", c_int),
        ("displacements", POINTER(c_int)),
        ("oldtype", c_short),
        ("newtype", c_short),
    ]

class DumpiTypeCreateResized(Structure):
    _fields_ = [
        ("oldtype", c_short),
        ("lb", c_int),
        ("extent", c_int),
        ("newtype", c_short),
    ]

class DumpiTypeCreateStruct(Structure):
    _fields_ = [
        ("count", c_int),
        ("blocklengths", POINTER(c_int)),
        ("displacements", POINTER(c_int)),
        ("oldtypes", POINTER(c_short)),
        ("newtype", c_short),
    ]

class DumpiTypeCreateSubarray(Structure):
    _fields_ = [
        ("ndims", c_int),
        ("sizes", POINTER(c_int)),
        ("subsizes", POINTER(c_int)),
        ("starts", POINTER(c_int)),
        ("order", c_byte),
        ("oldtype", c_short),
        ("newtype", c_short),
    ]

class DumpiTypeGetExtent(Structure):
    _fields_ = [
        ("datatype", c_short),
        ("lb", c_int),
        ("extent", c_int),
    ]

class DumpiTypeGetTrueExtent(Structure):
    _fields_ = [
        ("datatype", c_short),
        ("lb", c_int),
        ("extent", c_int),
    ]

class DumpiUnpackExternal(Structure):
    _fields_ = [
        ("datarep", POINTER(c_char)),
        ("insize", c_int),
        ("pos_in", c_int),
        ("pos_out", c_int),
        ("outcount", c_int),
        ("datatype", c_short),
    ]

class DumpiWinCreateErrhandler(Structure):
    _fields_ = [
        ("errhandler", c_short),
    ]

class DumpiWinGetErrhandler(Structure):
    _fields_ = [
        ("win", c_short),
        ("errhandler", c_short),
    ]

class DumpiWinSetErrhandler(Structure):
    _fields_ = [
        ("win", c_short),
        ("errhandler", c_short),
    ]

class DumpiFileOpen(Structure):
    _fields_ = [
        ("comm", c_short),
        ("filename", c_char_p),
        ("amode", c_short),
        ("info", c_short),
        ("file", c_short),
    ]

class DumpiFileClose(Structure):
    _fields_ = [
        ("file", c_short),
    ]

class DumpiFileDelete(Structure):
    _fields_ = [
        ("filename", c_char_p),
        ("info", c_short),
    ]

class DumpiFileSetSize(Structure):
    _fields_ = [
        ("file", c_short),
        ("size", c_longlong),
    ]

class DumpiFilePreallocate(Structure):
    _fields_ = [
        ("file", c_short),
        ("size", c_longlong),
    ]

class DumpiFileGetSize(Structure):
    _fields_ = [
        ("file", c_short),
        ("size", c_longlong),
    ]

class DumpiFileGetGroup(Structure):
    _fields_ = [
        ("file", c_short),
        ("group", c_short),
    ]

class DumpiFileGetAmode(Structure):
    _fields_ = [
        ("file", c_short),
        ("amode", c_short),
    ]

class DumpiFileSetInfo(Structure):
    _fields_ = [
        ("file", c_short),
        ("info", c_short),
    ]

class DumpiFileGetInfo(Structure):
    _fields_ = [
        ("file", c_short),
        ("info", c_short),
    ]

class DumpiFileSetView(Structure):
    _fields_ = [
        ("file", c_short),
        ("offset", c_longlong),
        ("hosttype", c_short),
        ("filetype", c_short),
        ("datarep", POINTER(c_char)),
        ("info", c_short),
    ]

class DumpiFileGetView(Structure):
    _fields_ = [
        ("file", c_short),
        ("offset", c_longlong),
        ("hosttype", c_short),
        ("filetype", c_short),
        ("datarep", POINTER(c_char)),
    ]

class DumpiFileReadAt(Structure):
    _fields_ = [
        ("file", c_short),
        ("offset", c_longlong),
        ("count", c_int),
        ("datatype", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileReadAtAll(Structure):
    _fields_ = [
        ("file", c_short),
        ("offset", c_longlong),
        ("count", c_int),
        ("datatype", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileWriteAt(Structure):
    _fields_ = [
        ("file", c_short),
        ("offset", c_longlong),
        ("count", c_int),
        ("datatype", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileWriteAtAll(Structure):
    _fields_ = [
        ("file", c_short),
        ("offset", c_longlong),
        ("count", c_int),
        ("datatype", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileIreadAt(Structure):
    _fields_ = [
        ("file", c_short),
        ("offset", c_longlong),
        ("count", c_int),
        ("datatype", c_short),
        ("request", c_int),
    ]

class DumpiFileIwriteAt(Structure):
    _fields_ = [
        ("file", c_short),
        ("offset", c_longlong),
        ("count", c_int),
        ("datatype", c_short),
        ("request", c_int),
    ]

class DumpiFileRead(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileReadAll(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileWrite(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileWriteAll(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileIread(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
        ("request", c_int),
    ]

class DumpiFileIwrite(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
        ("request", c_int),
    ]

class DumpiFileSeek(Structure):
    _fields_ = [
        ("file", c_short),
        ("offset", c_longlong),
        ("whence", c_short),
    ]

class DumpiFileGetPosition(Structure):
    _fields_ = [
        ("file", c_short),
        ("offset", c_longlong),
    ]

class DumpiFileGetByteOffset(Structure):
    _fields_ = [
        ("file", c_short),
        ("offset", c_longlong),
        ("bytes", c_longlong),
    ]

class DumpiFileReadShared(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileWriteShared(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileIreadShared(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
        ("request", c_int),
    ]

class DumpiFileIwriteShared(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
        ("request", c_int),
    ]

class DumpiFileReadOrdered(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileWriteOrdered(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileSeekShared(Structure):
    _fields_ = [
        ("file", c_short),
        ("offset", c_longlong),
        ("whence", c_short),
    ]

class DumpiFileGetPositionShared(Structure):
    _fields_ = [
        ("file", c_short),
        ("offset", c_longlong),
    ]

class DumpiFileReadAtAllBegin(Structure):
    _fields_ = [
        ("file", c_short),
        ("offset", c_longlong),
        ("count", c_int),
        ("datatype", c_short),
    ]

class DumpiFileReadAtAllEnd(Structure):
    _fields_ = [
        ("file", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileWriteAtAllBegin(Structure):
    _fields_ = [
        ("file", c_short),
        ("offset", c_longlong),
        ("count", c_int),
        ("datatype", c_short),
    ]

class DumpiFileWriteAtAllEnd(Structure):
    _fields_ = [
        ("file", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileReadAllBegin(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
    ]

class DumpiFileReadAllEnd(Structure):
    _fields_ = [
        ("file", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileWriteAllBegin(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
    ]

class DumpiFileWriteAllEnd(Structure):
    _fields_ = [
        ("file", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileReadOrderedBegin(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
    ]

class DumpiFileReadOrderedEnd(Structure):
    _fields_ = [
        ("file", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileWriteOrderedBegin(Structure):
    _fields_ = [
        ("file", c_short),
        ("count", c_int),
        ("datatype", c_short),
    ]

class DumpiFileWriteOrderedEnd(Structure):
    _fields_ = [
        ("file", c_short),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpiFileGetTypeExtent(Structure):
    _fields_ = [
        ("file", c_short),
        ("datatype", c_short),
        ("extent", c_int),
    ]

class DumpiRegisterDatarep(Structure):
    _fields_ = [
        ("name", c_char_p),
    ]

class DumpiFileSetAtomicity(Structure):
    _fields_ = [
        ("file", c_short),
        ("flag", c_int),
    ]

class DumpiFileGetAtomicity(Structure):
    _fields_ = [
        ("file", c_short),
        ("flag", c_int),
    ]

class DumpiFileSync(Structure):
    _fields_ = [
        ("file", c_short),
    ]

class DumpioTest(Structure):
    _fields_ = [
        ("request", c_int),
        ("flag", c_int),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpioWait(Structure):
    _fields_ = [
        ("request", c_int),
        ("status", POINTER(DumpiStatus)),
    ]

class DumpioTestAll(Structure):
    _fields_ = [
        ("count", c_int),
        ("requests", POINTER(c_int)),
        ("flag", c_int),
        ("statuses", POINTER(DumpiStatus)),
    ]

class DumpioWaitAll(Structure):
    _fields_ = [
        ("count", c_int),
        ("requests", POINTER(c_int)),
        ("statuses", POINTER(DumpiStatus)),
    ]

class DumpioTestAny(Structure):
    _fields_ = [
        ("count", c_int),
        ("requests", POINTER(c_int)),
        ("index", c_int),
        ("flag", c_int),
        ("statuses", POINTER(DumpiStatus)),
    ]

class DumpioWaitAny(Structure):
    _fields_ = [
        ("count", c_int),
        ("requests", POINTER(c_int)),
        ("index", c_int),
        ("statuses", POINTER(DumpiStatus)),
    ]

class DumpioWaitSome(Structure):
    _fields_ = [
        ("count", c_int),
        ("requests", POINTER(c_int)),
        ("outcount", c_int),
        ("indices", POINTER(c_int)),
        ("statuses", POINTER(DumpiStatus)),
    ]

class DumpioTestSome(Structure):
    _fields_ = [
        ("count", c_int),
        ("requests", POINTER(c_int)),
        ("outcount", c_int),
        ("indices", POINTER(c_int)),
        ("statuses", POINTER(DumpiStatus)),
    ]
