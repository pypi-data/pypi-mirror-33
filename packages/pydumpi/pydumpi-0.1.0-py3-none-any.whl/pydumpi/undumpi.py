from ctypes.util import find_library
from ctypes import cast, POINTER
from .callbacks import DumpiCallbacks, CALLBACK
from .constants import DataType
from .dtypes import *
from pathlib import Path
import traceback
import os.path
import time
import sys


undumpi = find_library("undumpi")
if undumpi is None:
    undumpi = Path(os.path.dirname(__file__)) / Path("lib") / "libundumpi.so.8.0.0"
    if not os.path.isfile(undumpi):
        raise ValueError("Could not find libundumpi!")

libundumpi = CDLL(undumpi)
libc = CDLL(find_library("c"))
undumpi_open = libundumpi.undumpi_open
undumpi_open.argtypes = [c_char_p]
undumpi_open.restype = POINTER(DumpiProfile)
undumpi_close = libundumpi.undumpi_close
undumpi_close.argtypes = [POINTER(DumpiProfile)]
undumpi_close.restype = c_int
undumpi_read_header = libundumpi.undumpi_read_header
undumpi_read_header.argtypes = [POINTER(DumpiProfile)]
undumpi_read_header.restype = POINTER(DumpiHeader)
undumpi_read_footer = libundumpi.undumpi_read_footer
undumpi_read_footer.argtypes = [POINTER(DumpiProfile)]
undumpi_read_footer.restype = POINTER(DumpiFooter)
undumpi_read_datatype_sizes = libundumpi.dumpi_read_datatype_sizes
undumpi_read_datatype_sizes.argtypes = [POINTER(DumpiProfile), POINTER(DumpiSizeof)]
undumpi_read_datatype_sizes.restype = c_int
undumpi_read_stream = libundumpi.undumpi_read_stream
undumpi_read_stream.argtypes = [POINTER(DumpiProfile), POINTER(DumpiCallbacks), c_void_p]
undumpi_read_stream.restype = c_int
undumpi_read_keyval_record = libundumpi.undumpi_read_keyval_record
undumpi_read_keyval_record.argtypes = [POINTER(DumpiProfile)]
undumpi_read_keyval_record.restype = POINTER(DumpiKeyvalRecord)
undumpi_clear_callbacks = libundumpi.libundumpi_clear_callbacks
undumpi_clear_callbacks.argtypes = [POINTER(DumpiCallbacks)]


class DumpiTrace:

    def __init__(self, file_name):
        self.file_name = file_name
        self._type_sizes = None
        self._profile = None

        self.cbacks = DumpiCallbacks()
        undumpi_clear_callbacks(byref(self.cbacks))

        if hasattr(self, "on_send"):
            self.cbacks.on_send = CALLBACK(self.__on_send)
        if hasattr(self, "on_recv"):
            self.cbacks.on_recv = CALLBACK(self.__on_recv)
        if hasattr(self, "on_get_count"):
            self.cbacks.on_get_count = CALLBACK(self.__on_get_count)
        if hasattr(self, "on_bsend"):
            self.cbacks.on_bsend = CALLBACK(self.__on_bsend)
        if hasattr(self, "on_ssend"):
            self.cbacks.on_ssend = CALLBACK(self.__on_ssend)
        if hasattr(self, "on_rsend"):
            self.cbacks.on_rsend = CALLBACK(self.__on_rsend)
        if hasattr(self, "on_buffer_attach"):
            self.cbacks.on_buffer_attach = CALLBACK(self.__on_buffer_attach)
        if hasattr(self, "on_buffer_detach"):
            self.cbacks.on_buffer_detach = CALLBACK(self.__on_buffer_detach)
        if hasattr(self, "on_isend"):
            self.cbacks.on_isend = CALLBACK(self.__on_isend)
        if hasattr(self, "on_ibsend"):
            self.cbacks.on_ibsend = CALLBACK(self.__on_ibsend)
        if hasattr(self, "on_issend"):
            self.cbacks.on_issend = CALLBACK(self.__on_issend)
        if hasattr(self, "on_irsend"):
            self.cbacks.on_irsend = CALLBACK(self.__on_irsend)
        if hasattr(self, "on_irecv"):
            self.cbacks.on_irecv = CALLBACK(self.__on_irecv)
        if hasattr(self, "on_wait"):
            self.cbacks.on_wait = CALLBACK(self.__on_wait)
        if hasattr(self, "on_test"):
            self.cbacks.on_test = CALLBACK(self.__on_test)
        if hasattr(self, "on_request_free"):
            self.cbacks.on_request_free = CALLBACK(self.__on_request_free)
        if hasattr(self, "on_waitany"):
            self.cbacks.on_waitany = CALLBACK(self.__on_waitany)
        if hasattr(self, "on_testany"):
            self.cbacks.on_testany = CALLBACK(self.__on_testany)
        if hasattr(self, "on_waitall"):
            self.cbacks.on_waitall = CALLBACK(self.__on_waitall)
        if hasattr(self, "on_testall"):
            self.cbacks.on_testall = CALLBACK(self.__on_testall)
        if hasattr(self, "on_waitsome"):
            self.cbacks.on_waitsome = CALLBACK(self.__on_waitsome)
        if hasattr(self, "on_testsome"):
            self.cbacks.on_testsome = CALLBACK(self.__on_testsome)
        if hasattr(self, "on_iprobe"):
            self.cbacks.on_iprobe = CALLBACK(self.__on_iprobe)
        if hasattr(self, "on_probe"):
            self.cbacks.on_probe = CALLBACK(self.__on_probe)
        if hasattr(self, "on_cancel"):
            self.cbacks.on_cancel = CALLBACK(self.__on_cancel)
        if hasattr(self, "on_test_cancelled"):
            self.cbacks.on_test_cancelled = CALLBACK(self.__on_test_cancelled)
        if hasattr(self, "on_send_init"):
            self.cbacks.on_send_init = CALLBACK(self.__on_send_init)
        if hasattr(self, "on_bsend_init"):
            self.cbacks.on_bsend_init = CALLBACK(self.__on_bsend_init)
        if hasattr(self, "on_ssend_init"):
            self.cbacks.on_ssend_init = CALLBACK(self.__on_ssend_init)
        if hasattr(self, "on_rsend_init"):
            self.cbacks.on_rsend_init = CALLBACK(self.__on_rsend_init)
        if hasattr(self, "on_recv_init"):
            self.cbacks.on_recv_init = CALLBACK(self.__on_recv_init)
        if hasattr(self, "on_start"):
            self.cbacks.on_start = CALLBACK(self.__on_start)
        if hasattr(self, "on_startall"):
            self.cbacks.on_startall = CALLBACK(self.__on_startall)
        if hasattr(self, "on_sendrecv"):
            self.cbacks.on_sendrecv = CALLBACK(self.__on_sendrecv)
        if hasattr(self, "on_sendrecv_replace"):
            self.cbacks.on_sendrecv_replace = CALLBACK(self.__on_sendrecv_replace)
        if hasattr(self, "on_type_contiguous"):
            self.cbacks.on_type_contiguous = CALLBACK(self.__on_type_contiguous)
        if hasattr(self, "on_type_vector"):
            self.cbacks.on_type_vector = CALLBACK(self.__on_type_vector)
        if hasattr(self, "on_type_hvector"):
            self.cbacks.on_type_hvector = CALLBACK(self.__on_type_hvector)
        if hasattr(self, "on_type_indexed"):
            self.cbacks.on_type_indexed = CALLBACK(self.__on_type_indexed)
        if hasattr(self, "on_type_hindexed"):
            self.cbacks.on_type_hindexed = CALLBACK(self.__on_type_hindexed)
        if hasattr(self, "on_type_struct"):
            self.cbacks.on_type_struct = CALLBACK(self.__on_type_struct)
        if hasattr(self, "on_address"):
            self.cbacks.on_address = CALLBACK(self.__on_address)
        if hasattr(self, "on_type_extent"):
            self.cbacks.on_type_extent = CALLBACK(self.__on_type_extent)
        if hasattr(self, "on_type_size"):
            self.cbacks.on_type_size = CALLBACK(self.__on_type_size)
        if hasattr(self, "on_type_lb"):
            self.cbacks.on_type_lb = CALLBACK(self.__on_type_lb)
        if hasattr(self, "on_type_ub"):
            self.cbacks.on_type_ub = CALLBACK(self.__on_type_ub)
        if hasattr(self, "on_type_commit"):
            self.cbacks.on_type_commit = CALLBACK(self.__on_type_commit)
        if hasattr(self, "on_type_free"):
            self.cbacks.on_type_free = CALLBACK(self.__on_type_free)
        if hasattr(self, "on_get_elements"):
            self.cbacks.on_get_elements = CALLBACK(self.__on_get_elements)
        if hasattr(self, "on_pack"):
            self.cbacks.on_pack = CALLBACK(self.__on_pack)
        if hasattr(self, "on_unpack"):
            self.cbacks.on_unpack = CALLBACK(self.__on_unpack)
        if hasattr(self, "on_pack_size"):
            self.cbacks.on_pack_size = CALLBACK(self.__on_pack_size)
        if hasattr(self, "on_barrier"):
            self.cbacks.on_barrier = CALLBACK(self.__on_barrier)
        if hasattr(self, "on_bcast"):
            self.cbacks.on_bcast = CALLBACK(self.__on_bcast)
        if hasattr(self, "on_gather"):
            self.cbacks.on_gather = CALLBACK(self.__on_gather)
        if hasattr(self, "on_gatherv"):
            self.cbacks.on_gatherv = CALLBACK(self.__on_gatherv)
        if hasattr(self, "on_scatter"):
            self.cbacks.on_scatter = CALLBACK(self.__on_scatter)
        if hasattr(self, "on_scatterv"):
            self.cbacks.on_scatterv = CALLBACK(self.__on_scatterv)
        if hasattr(self, "on_allgather"):
            self.cbacks.on_allgather = CALLBACK(self.__on_allgather)
        if hasattr(self, "on_allgatherv"):
            self.cbacks.on_allgatherv = CALLBACK(self.__on_allgatherv)
        if hasattr(self, "on_alltoall"):
            self.cbacks.on_alltoall = CALLBACK(self.__on_alltoall)
        if hasattr(self, "on_alltoallv"):
            self.cbacks.on_alltoallv = CALLBACK(self.__on_alltoallv)
        if hasattr(self, "on_reduce"):
            self.cbacks.on_reduce = CALLBACK(self.__on_reduce)
        if hasattr(self, "on_op_create"):
            self.cbacks.on_op_create = CALLBACK(self.__on_op_create)
        if hasattr(self, "on_op_free"):
            self.cbacks.on_op_free = CALLBACK(self.__on_op_free)
        if hasattr(self, "on_allreduce"):
            self.cbacks.on_allreduce = CALLBACK(self.__on_allreduce)
        if hasattr(self, "on_reduce_scatter"):
            self.cbacks.on_reduce_scatter = CALLBACK(self.__on_reduce_scatter)
        if hasattr(self, "on_scan"):
            self.cbacks.on_scan = CALLBACK(self.__on_scan)
        if hasattr(self, "on_group_size"):
            self.cbacks.on_group_size = CALLBACK(self.__on_group_size)
        if hasattr(self, "on_group_rank"):
            self.cbacks.on_group_rank = CALLBACK(self.__on_group_rank)
        if hasattr(self, "on_group_translate_ranks"):
            self.cbacks.on_group_translate_ranks = CALLBACK(self.__on_group_translate_ranks)
        if hasattr(self, "on_group_compare"):
            self.cbacks.on_group_compare = CALLBACK(self.__on_group_compare)
        if hasattr(self, "on_comm_group"):
            self.cbacks.on_comm_group = CALLBACK(self.__on_comm_group)
        if hasattr(self, "on_group_union"):
            self.cbacks.on_group_union = CALLBACK(self.__on_group_union)
        if hasattr(self, "on_group_intersection"):
            self.cbacks.on_group_intersection = CALLBACK(self.__on_group_intersection)
        if hasattr(self, "on_group_difference"):
            self.cbacks.on_group_difference = CALLBACK(self.__on_group_difference)
        if hasattr(self, "on_group_incl"):
            self.cbacks.on_group_incl = CALLBACK(self.__on_group_incl)
        if hasattr(self, "on_group_excl"):
            self.cbacks.on_group_excl = CALLBACK(self.__on_group_excl)
        if hasattr(self, "on_group_range_incl"):
            self.cbacks.on_group_range_incl = CALLBACK(self.__on_group_range_incl)
        if hasattr(self, "on_group_range_excl"):
            self.cbacks.on_group_range_excl = CALLBACK(self.__on_group_range_excl)
        if hasattr(self, "on_group_free"):
            self.cbacks.on_group_free = CALLBACK(self.__on_group_free)
        if hasattr(self, "on_comm_size"):
            self.cbacks.on_comm_size = CALLBACK(self.__on_comm_size)
        if hasattr(self, "on_comm_rank"):
            self.cbacks.on_comm_rank = CALLBACK(self.__on_comm_rank)
        if hasattr(self, "on_comm_compare"):
            self.cbacks.on_comm_compare = CALLBACK(self.__on_comm_compare)
        if hasattr(self, "on_comm_dup"):
            self.cbacks.on_comm_dup = CALLBACK(self.__on_comm_dup)
        if hasattr(self, "on_comm_create"):
            self.cbacks.on_comm_create = CALLBACK(self.__on_comm_create)
        if hasattr(self, "on_comm_split"):
            self.cbacks.on_comm_split = CALLBACK(self.__on_comm_split)
        if hasattr(self, "on_comm_free"):
            self.cbacks.on_comm_free = CALLBACK(self.__on_comm_free)
        if hasattr(self, "on_comm_test_inter"):
            self.cbacks.on_comm_test_inter = CALLBACK(self.__on_comm_test_inter)
        if hasattr(self, "on_comm_remote_size"):
            self.cbacks.on_comm_remote_size = CALLBACK(self.__on_comm_remote_size)
        if hasattr(self, "on_comm_remote_group"):
            self.cbacks.on_comm_remote_group = CALLBACK(self.__on_comm_remote_group)
        if hasattr(self, "on_intercomm_create"):
            self.cbacks.on_intercomm_create = CALLBACK(self.__on_intercomm_create)
        if hasattr(self, "on_intercomm_merge"):
            self.cbacks.on_intercomm_merge = CALLBACK(self.__on_intercomm_merge)
        if hasattr(self, "on_keyval_create"):
            self.cbacks.on_keyval_create = CALLBACK(self.__on_keyval_create)
        if hasattr(self, "on_keyval_free"):
            self.cbacks.on_keyval_free = CALLBACK(self.__on_keyval_free)
        if hasattr(self, "on_attr_put"):
            self.cbacks.on_attr_put = CALLBACK(self.__on_attr_put)
        if hasattr(self, "on_attr_get"):
            self.cbacks.on_attr_get = CALLBACK(self.__on_attr_get)
        if hasattr(self, "on_attr_delete"):
            self.cbacks.on_attr_delete = CALLBACK(self.__on_attr_delete)
        if hasattr(self, "on_topo_test"):
            self.cbacks.on_topo_test = CALLBACK(self.__on_topo_test)
        if hasattr(self, "on_cart_create"):
            self.cbacks.on_cart_create = CALLBACK(self.__on_cart_create)
        if hasattr(self, "on_dims_create"):
            self.cbacks.on_dims_create = CALLBACK(self.__on_dims_create)
        if hasattr(self, "on_graph_create"):
            self.cbacks.on_graph_create = CALLBACK(self.__on_graph_create)
        if hasattr(self, "on_graphdims_get"):
            self.cbacks.on_graphdims_get = CALLBACK(self.__on_graphdims_get)
        if hasattr(self, "on_graph_get"):
            self.cbacks.on_graph_get = CALLBACK(self.__on_graph_get)
        if hasattr(self, "on_cartdim_get"):
            self.cbacks.on_cartdim_get = CALLBACK(self.__on_cartdim_get)
        if hasattr(self, "on_cart_get"):
            self.cbacks.on_cart_get = CALLBACK(self.__on_cart_get)
        if hasattr(self, "on_cart_rank"):
            self.cbacks.on_cart_rank = CALLBACK(self.__on_cart_rank)
        if hasattr(self, "on_cart_coords"):
            self.cbacks.on_cart_coords = CALLBACK(self.__on_cart_coords)
        if hasattr(self, "on_graph_neighbors_count"):
            self.cbacks.on_graph_neighbors_count = CALLBACK(self.__on_graph_neighbors_count)
        if hasattr(self, "on_graph_neighbors"):
            self.cbacks.on_graph_neighbors = CALLBACK(self.__on_graph_neighbors)
        if hasattr(self, "on_cart_shift"):
            self.cbacks.on_cart_shift = CALLBACK(self.__on_cart_shift)
        if hasattr(self, "on_cart_sub"):
            self.cbacks.on_cart_sub = CALLBACK(self.__on_cart_sub)
        if hasattr(self, "on_cart_map"):
            self.cbacks.on_cart_map = CALLBACK(self.__on_cart_map)
        if hasattr(self, "on_graph_map"):
            self.cbacks.on_graph_map = CALLBACK(self.__on_graph_map)
        if hasattr(self, "on_get_processor_name"):
            self.cbacks.on_get_processor_name = CALLBACK(self.__on_get_processor_name)
        if hasattr(self, "on_get_version"):
            self.cbacks.on_get_version = CALLBACK(self.__on_get_version)
        if hasattr(self, "on_errhandler_create"):
            self.cbacks.on_errhandler_create = CALLBACK(self.__on_errhandler_create)
        if hasattr(self, "on_errhandler_set"):
            self.cbacks.on_errhandler_set = CALLBACK(self.__on_errhandler_set)
        if hasattr(self, "on_errhandler_get"):
            self.cbacks.on_errhandler_get = CALLBACK(self.__on_errhandler_get)
        if hasattr(self, "on_errhandler_free"):
            self.cbacks.on_errhandler_free = CALLBACK(self.__on_errhandler_free)
        if hasattr(self, "on_error_string"):
            self.cbacks.on_error_string = CALLBACK(self.__on_error_string)
        if hasattr(self, "on_error_class"):
            self.cbacks.on_error_class = CALLBACK(self.__on_error_class)
        if hasattr(self, "on_wtime"):
            self.cbacks.on_wtime = CALLBACK(self.__on_wtime)
        if hasattr(self, "on_wtick"):
            self.cbacks.on_wtick = CALLBACK(self.__on_wtick)
        if hasattr(self, "on_init"):
            self.cbacks.on_init = CALLBACK(self.__on_init)
        if hasattr(self, "on_finalize"):
            self.cbacks.on_finalize = CALLBACK(self.__on_finalize)
        if hasattr(self, "on_initialized"):
            self.cbacks.on_initialized = CALLBACK(self.__on_initialized)
        if hasattr(self, "on_abort"):
            self.cbacks.on_abort = CALLBACK(self.__on_abort)
        if hasattr(self, "on_close_port"):
            self.cbacks.on_close_port = CALLBACK(self.__on_close_port)
        if hasattr(self, "on_comm_accept"):
            self.cbacks.on_comm_accept = CALLBACK(self.__on_comm_accept)
        if hasattr(self, "on_comm_connect"):
            self.cbacks.on_comm_connect = CALLBACK(self.__on_comm_connect)
        if hasattr(self, "on_comm_disconnect"):
            self.cbacks.on_comm_disconnect = CALLBACK(self.__on_comm_disconnect)
        if hasattr(self, "on_comm_get_parent"):
            self.cbacks.on_comm_get_parent = CALLBACK(self.__on_comm_get_parent)
        if hasattr(self, "on_comm_join"):
            self.cbacks.on_comm_join = CALLBACK(self.__on_comm_join)
        if hasattr(self, "on_comm_spawn"):
            self.cbacks.on_comm_spawn = CALLBACK(self.__on_comm_spawn)
        if hasattr(self, "on_comm_spawn_multiple"):
            self.cbacks.on_comm_spawn_multiple = CALLBACK(self.__on_comm_spawn_multiple)
        if hasattr(self, "on_lookup_name"):
            self.cbacks.on_lookup_name = CALLBACK(self.__on_lookup_name)
        if hasattr(self, "on_open_port"):
            self.cbacks.on_open_port = CALLBACK(self.__on_open_port)
        if hasattr(self, "on_publish_name"):
            self.cbacks.on_publish_name = CALLBACK(self.__on_publish_name)
        if hasattr(self, "on_unpublish_name"):
            self.cbacks.on_unpublish_name = CALLBACK(self.__on_unpublish_name)
        if hasattr(self, "on_accumulate"):
            self.cbacks.on_accumulate = CALLBACK(self.__on_accumulate)
        if hasattr(self, "on_get"):
            self.cbacks.on_get = CALLBACK(self.__on_get)
        if hasattr(self, "on_put"):
            self.cbacks.on_put = CALLBACK(self.__on_put)
        if hasattr(self, "on_win_complete"):
            self.cbacks.on_win_complete = CALLBACK(self.__on_win_complete)
        if hasattr(self, "on_win_create"):
            self.cbacks.on_win_create = CALLBACK(self.__on_win_create)
        if hasattr(self, "on_win_fence"):
            self.cbacks.on_win_fence = CALLBACK(self.__on_win_fence)
        if hasattr(self, "on_win_free"):
            self.cbacks.on_win_free = CALLBACK(self.__on_win_free)
        if hasattr(self, "on_win_get_group"):
            self.cbacks.on_win_get_group = CALLBACK(self.__on_win_get_group)
        if hasattr(self, "on_win_lock"):
            self.cbacks.on_win_lock = CALLBACK(self.__on_win_lock)
        if hasattr(self, "on_win_post"):
            self.cbacks.on_win_post = CALLBACK(self.__on_win_post)
        if hasattr(self, "on_win_start"):
            self.cbacks.on_win_start = CALLBACK(self.__on_win_start)
        if hasattr(self, "on_win_test"):
            self.cbacks.on_win_test = CALLBACK(self.__on_win_test)
        if hasattr(self, "on_win_unlock"):
            self.cbacks.on_win_unlock = CALLBACK(self.__on_win_unlock)
        if hasattr(self, "on_win_wait"):
            self.cbacks.on_win_wait = CALLBACK(self.__on_win_wait)
        if hasattr(self, "on_alltoallw"):
            self.cbacks.on_alltoallw = CALLBACK(self.__on_alltoallw)
        if hasattr(self, "on_exscan"):
            self.cbacks.on_exscan = CALLBACK(self.__on_exscan)
        if hasattr(self, "on_add_error_class"):
            self.cbacks.on_add_error_class = CALLBACK(self.__on_add_error_class)
        if hasattr(self, "on_add_error_code"):
            self.cbacks.on_add_error_code = CALLBACK(self.__on_add_error_code)
        if hasattr(self, "on_add_error_string"):
            self.cbacks.on_add_error_string = CALLBACK(self.__on_add_error_string)
        if hasattr(self, "on_comm_call_errhandler"):
            self.cbacks.on_comm_call_errhandler = CALLBACK(self.__on_comm_call_errhandler)
        if hasattr(self, "on_comm_create_keyval"):
            self.cbacks.on_comm_create_keyval = CALLBACK(self.__on_comm_create_keyval)
        if hasattr(self, "on_comm_delete_attr"):
            self.cbacks.on_comm_delete_attr = CALLBACK(self.__on_comm_delete_attr)
        if hasattr(self, "on_comm_free_keyval"):
            self.cbacks.on_comm_free_keyval = CALLBACK(self.__on_comm_free_keyval)
        if hasattr(self, "on_comm_get_attr"):
            self.cbacks.on_comm_get_attr = CALLBACK(self.__on_comm_get_attr)
        if hasattr(self, "on_comm_get_name"):
            self.cbacks.on_comm_get_name = CALLBACK(self.__on_comm_get_name)
        if hasattr(self, "on_comm_set_attr"):
            self.cbacks.on_comm_set_attr = CALLBACK(self.__on_comm_set_attr)
        if hasattr(self, "on_comm_set_name"):
            self.cbacks.on_comm_set_name = CALLBACK(self.__on_comm_set_name)
        if hasattr(self, "on_file_call_errhandler"):
            self.cbacks.on_file_call_errhandler = CALLBACK(self.__on_file_call_errhandler)
        if hasattr(self, "on_grequest_complete"):
            self.cbacks.on_grequest_complete = CALLBACK(self.__on_grequest_complete)
        if hasattr(self, "on_grequest_start"):
            self.cbacks.on_grequest_start = CALLBACK(self.__on_grequest_start)
        if hasattr(self, "on_init_thread"):
            self.cbacks.on_init_thread = CALLBACK(self.__on_init_thread)
        if hasattr(self, "on_is_thread_main"):
            self.cbacks.on_is_thread_main = CALLBACK(self.__on_is_thread_main)
        if hasattr(self, "on_query_thread"):
            self.cbacks.on_query_thread = CALLBACK(self.__on_query_thread)
        if hasattr(self, "on_status_set_cancelled"):
            self.cbacks.on_status_set_cancelled = CALLBACK(self.__on_status_set_cancelled)
        if hasattr(self, "on_status_set_elements"):
            self.cbacks.on_status_set_elements = CALLBACK(self.__on_status_set_elements)
        if hasattr(self, "on_type_create_keyval"):
            self.cbacks.on_type_create_keyval = CALLBACK(self.__on_type_create_keyval)
        if hasattr(self, "on_type_delete_attr"):
            self.cbacks.on_type_delete_attr = CALLBACK(self.__on_type_delete_attr)
        if hasattr(self, "on_type_dup"):
            self.cbacks.on_type_dup = CALLBACK(self.__on_type_dup)
        if hasattr(self, "on_type_free_keyval"):
            self.cbacks.on_type_free_keyval = CALLBACK(self.__on_type_free_keyval)
        if hasattr(self, "on_type_get_attr"):
            self.cbacks.on_type_get_attr = CALLBACK(self.__on_type_get_attr)
        if hasattr(self, "on_type_get_contents"):
            self.cbacks.on_type_get_contents = CALLBACK(self.__on_type_get_contents)
        if hasattr(self, "on_type_get_envelope"):
            self.cbacks.on_type_get_envelope = CALLBACK(self.__on_type_get_envelope)
        if hasattr(self, "on_type_get_name"):
            self.cbacks.on_type_get_name = CALLBACK(self.__on_type_get_name)
        if hasattr(self, "on_type_set_attr"):
            self.cbacks.on_type_set_attr = CALLBACK(self.__on_type_set_attr)
        if hasattr(self, "on_type_set_name"):
            self.cbacks.on_type_set_name = CALLBACK(self.__on_type_set_name)
        if hasattr(self, "on_type_match_size"):
            self.cbacks.on_type_match_size = CALLBACK(self.__on_type_match_size)
        if hasattr(self, "on_win_call_errhandler"):
            self.cbacks.on_win_call_errhandler = CALLBACK(self.__on_win_call_errhandler)
        if hasattr(self, "on_win_create_keyval"):
            self.cbacks.on_win_create_keyval = CALLBACK(self.__on_win_create_keyval)
        if hasattr(self, "on_win_delete_attr"):
            self.cbacks.on_win_delete_attr = CALLBACK(self.__on_win_delete_attr)
        if hasattr(self, "on_win_free_keyval"):
            self.cbacks.on_win_free_keyval = CALLBACK(self.__on_win_free_keyval)
        if hasattr(self, "on_win_get_attr"):
            self.cbacks.on_win_get_attr = CALLBACK(self.__on_win_get_attr)
        if hasattr(self, "on_win_get_name"):
            self.cbacks.on_win_get_name = CALLBACK(self.__on_win_get_name)
        if hasattr(self, "on_win_set_attr"):
            self.cbacks.on_win_set_attr = CALLBACK(self.__on_win_set_attr)
        if hasattr(self, "on_win_set_name"):
            self.cbacks.on_win_set_name = CALLBACK(self.__on_win_set_name)
        if hasattr(self, "on_alloc_mem"):
            self.cbacks.on_alloc_mem = CALLBACK(self.__on_alloc_mem)
        if hasattr(self, "on_comm_create_errhandler"):
            self.cbacks.on_comm_create_errhandler = CALLBACK(self.__on_comm_create_errhandler)
        if hasattr(self, "on_comm_get_errhandler"):
            self.cbacks.on_comm_get_errhandler = CALLBACK(self.__on_comm_get_errhandler)
        if hasattr(self, "on_comm_set_errhandler"):
            self.cbacks.on_comm_set_errhandler = CALLBACK(self.__on_comm_set_errhandler)
        if hasattr(self, "on_file_create_errhandler"):
            self.cbacks.on_file_create_errhandler = CALLBACK(self.__on_file_create_errhandler)
        if hasattr(self, "on_file_get_errhandler"):
            self.cbacks.on_file_get_errhandler = CALLBACK(self.__on_file_get_errhandler)
        if hasattr(self, "on_file_set_errhandler"):
            self.cbacks.on_file_set_errhandler = CALLBACK(self.__on_file_set_errhandler)
        if hasattr(self, "on_finalized"):
            self.cbacks.on_finalized = CALLBACK(self.__on_finalized)
        if hasattr(self, "on_free_mem"):
            self.cbacks.on_free_mem = CALLBACK(self.__on_free_mem)
        if hasattr(self, "on_get_address"):
            self.cbacks.on_get_address = CALLBACK(self.__on_get_address)
        if hasattr(self, "on_info_create"):
            self.cbacks.on_info_create = CALLBACK(self.__on_info_create)
        if hasattr(self, "on_info_delete"):
            self.cbacks.on_info_delete = CALLBACK(self.__on_info_delete)
        if hasattr(self, "on_info_dup"):
            self.cbacks.on_info_dup = CALLBACK(self.__on_info_dup)
        if hasattr(self, "on_info_free"):
            self.cbacks.on_info_free = CALLBACK(self.__on_info_free)
        if hasattr(self, "on_info_get"):
            self.cbacks.on_info_get = CALLBACK(self.__on_info_get)
        if hasattr(self, "on_info_get_nkeys"):
            self.cbacks.on_info_get_nkeys = CALLBACK(self.__on_info_get_nkeys)
        if hasattr(self, "on_info_get_nthkey"):
            self.cbacks.on_info_get_nthkey = CALLBACK(self.__on_info_get_nthkey)
        if hasattr(self, "on_info_get_valuelen"):
            self.cbacks.on_info_get_valuelen = CALLBACK(self.__on_info_get_valuelen)
        if hasattr(self, "on_info_set"):
            self.cbacks.on_info_set = CALLBACK(self.__on_info_set)
        if hasattr(self, "on_pack_external"):
            self.cbacks.on_pack_external = CALLBACK(self.__on_pack_external)
        if hasattr(self, "on_pack_external_size"):
            self.cbacks.on_pack_external_size = CALLBACK(self.__on_pack_external_size)
        if hasattr(self, "on_request_get_status"):
            self.cbacks.on_request_get_status = CALLBACK(self.__on_request_get_status)
        if hasattr(self, "on_type_create_darray"):
            self.cbacks.on_type_create_darray = CALLBACK(self.__on_type_create_darray)
        if hasattr(self, "on_type_create_hindexed"):
            self.cbacks.on_type_create_hindexed = CALLBACK(self.__on_type_create_hindexed)
        if hasattr(self, "on_type_create_hvector"):
            self.cbacks.on_type_create_hvector = CALLBACK(self.__on_type_create_hvector)
        if hasattr(self, "on_type_create_indexed_block"):
            self.cbacks.on_type_create_indexed_block = CALLBACK(self.__on_type_create_indexed_block)
        if hasattr(self, "on_type_create_resized"):
            self.cbacks.on_type_create_resized = CALLBACK(self.__on_type_create_resized)
        if hasattr(self, "on_type_create_struct"):
            self.cbacks.on_type_create_struct = CALLBACK(self.__on_type_create_struct)
        if hasattr(self, "on_type_create_subarray"):
            self.cbacks.on_type_create_subarray = CALLBACK(self.__on_type_create_subarray)
        if hasattr(self, "on_type_get_extent"):
            self.cbacks.on_type_get_extent = CALLBACK(self.__on_type_get_extent)
        if hasattr(self, "on_type_get_true_extent"):
            self.cbacks.on_type_get_true_extent = CALLBACK(self.__on_type_get_true_extent)
        if hasattr(self, "on_unpack_external"):
            self.cbacks.on_unpack_external = CALLBACK(self.__on_unpack_external)
        if hasattr(self, "on_win_create_errhandler"):
            self.cbacks.on_win_create_errhandler = CALLBACK(self.__on_win_create_errhandler)
        if hasattr(self, "on_win_get_errhandler"):
            self.cbacks.on_win_get_errhandler = CALLBACK(self.__on_win_get_errhandler)
        if hasattr(self, "on_win_set_errhandler"):
            self.cbacks.on_win_set_errhandler = CALLBACK(self.__on_win_set_errhandler)
        if hasattr(self, "on_file_open"):
            self.cbacks.on_file_open = CALLBACK(self.__on_file_open)
        if hasattr(self, "on_file_close"):
            self.cbacks.on_file_close = CALLBACK(self.__on_file_close)
        if hasattr(self, "on_file_delete"):
            self.cbacks.on_file_delete = CALLBACK(self.__on_file_delete)
        if hasattr(self, "on_file_set_size"):
            self.cbacks.on_file_set_size = CALLBACK(self.__on_file_set_size)
        if hasattr(self, "on_file_preallocate"):
            self.cbacks.on_file_preallocate = CALLBACK(self.__on_file_preallocate)
        if hasattr(self, "on_file_get_size"):
            self.cbacks.on_file_get_size = CALLBACK(self.__on_file_get_size)
        if hasattr(self, "on_file_get_group"):
            self.cbacks.on_file_get_group = CALLBACK(self.__on_file_get_group)
        if hasattr(self, "on_file_get_amode"):
            self.cbacks.on_file_get_amode = CALLBACK(self.__on_file_get_amode)
        if hasattr(self, "on_file_set_info"):
            self.cbacks.on_file_set_info = CALLBACK(self.__on_file_set_info)
        if hasattr(self, "on_file_get_info"):
            self.cbacks.on_file_get_info = CALLBACK(self.__on_file_get_info)
        if hasattr(self, "on_file_set_view"):
            self.cbacks.on_file_set_view = CALLBACK(self.__on_file_set_view)
        if hasattr(self, "on_file_get_view"):
            self.cbacks.on_file_get_view = CALLBACK(self.__on_file_get_view)
        if hasattr(self, "on_file_read_at"):
            self.cbacks.on_file_read_at = CALLBACK(self.__on_file_read_at)
        if hasattr(self, "on_file_read_at_all"):
            self.cbacks.on_file_read_at_all = CALLBACK(self.__on_file_read_at_all)
        if hasattr(self, "on_file_write_at"):
            self.cbacks.on_file_write_at = CALLBACK(self.__on_file_write_at)
        if hasattr(self, "on_file_write_at_all"):
            self.cbacks.on_file_write_at_all = CALLBACK(self.__on_file_write_at_all)
        if hasattr(self, "on_file_iread_at"):
            self.cbacks.on_file_iread_at = CALLBACK(self.__on_file_iread_at)
        if hasattr(self, "on_file_iwrite_at"):
            self.cbacks.on_file_iwrite_at = CALLBACK(self.__on_file_iwrite_at)
        if hasattr(self, "on_file_read"):
            self.cbacks.on_file_read = CALLBACK(self.__on_file_read)
        if hasattr(self, "on_file_read_all"):
            self.cbacks.on_file_read_all = CALLBACK(self.__on_file_read_all)
        if hasattr(self, "on_file_write"):
            self.cbacks.on_file_write = CALLBACK(self.__on_file_write)
        if hasattr(self, "on_file_write_all"):
            self.cbacks.on_file_write_all = CALLBACK(self.__on_file_write_all)
        if hasattr(self, "on_file_iread"):
            self.cbacks.on_file_iread = CALLBACK(self.__on_file_iread)
        if hasattr(self, "on_file_iwrite"):
            self.cbacks.on_file_iwrite = CALLBACK(self.__on_file_iwrite)
        if hasattr(self, "on_file_seek"):
            self.cbacks.on_file_seek = CALLBACK(self.__on_file_seek)
        if hasattr(self, "on_file_get_position"):
            self.cbacks.on_file_get_position = CALLBACK(self.__on_file_get_position)
        if hasattr(self, "on_file_get_byte_offset"):
            self.cbacks.on_file_get_byte_offset = CALLBACK(self.__on_file_get_byte_offset)
        if hasattr(self, "on_file_read_shared"):
            self.cbacks.on_file_read_shared = CALLBACK(self.__on_file_read_shared)
        if hasattr(self, "on_file_write_shared"):
            self.cbacks.on_file_write_shared = CALLBACK(self.__on_file_write_shared)
        if hasattr(self, "on_file_iread_shared"):
            self.cbacks.on_file_iread_shared = CALLBACK(self.__on_file_iread_shared)
        if hasattr(self, "on_file_iwrite_shared"):
            self.cbacks.on_file_iwrite_shared = CALLBACK(self.__on_file_iwrite_shared)
        if hasattr(self, "on_file_read_ordered"):
            self.cbacks.on_file_read_ordered = CALLBACK(self.__on_file_read_ordered)
        if hasattr(self, "on_file_write_ordered"):
            self.cbacks.on_file_write_ordered = CALLBACK(self.__on_file_write_ordered)
        if hasattr(self, "on_file_seek_shared"):
            self.cbacks.on_file_seek_shared = CALLBACK(self.__on_file_seek_shared)
        if hasattr(self, "on_file_get_position_shared"):
            self.cbacks.on_file_get_position_shared = CALLBACK(self.__on_file_get_position_shared)
        if hasattr(self, "on_file_read_at_all_begin"):
            self.cbacks.on_file_read_at_all_begin = CALLBACK(self.__on_file_read_at_all_begin)
        if hasattr(self, "on_file_read_at_all_end"):
            self.cbacks.on_file_read_at_all_end = CALLBACK(self.__on_file_read_at_all_end)
        if hasattr(self, "on_file_write_at_all_begin"):
            self.cbacks.on_file_write_at_all_begin = CALLBACK(self.__on_file_write_at_all_begin)
        if hasattr(self, "on_file_write_at_all_end"):
            self.cbacks.on_file_write_at_all_end = CALLBACK(self.__on_file_write_at_all_end)
        if hasattr(self, "on_file_read_all_begin"):
            self.cbacks.on_file_read_all_begin = CALLBACK(self.__on_file_read_all_begin)
        if hasattr(self, "on_file_read_all_end"):
            self.cbacks.on_file_read_all_end = CALLBACK(self.__on_file_read_all_end)
        if hasattr(self, "on_file_write_all_begin"):
            self.cbacks.on_file_write_all_begin = CALLBACK(self.__on_file_write_all_begin)
        if hasattr(self, "on_file_write_all_end"):
            self.cbacks.on_file_write_all_end = CALLBACK(self.__on_file_write_all_end)
        if hasattr(self, "on_file_read_ordered_begin"):
            self.cbacks.on_file_read_ordered_begin = CALLBACK(self.__on_file_read_ordered_begin)
        if hasattr(self, "on_file_read_ordered_end"):
            self.cbacks.on_file_read_ordered_end = CALLBACK(self.__on_file_read_ordered_end)
        if hasattr(self, "on_file_write_ordered_begin"):
            self.cbacks.on_file_write_ordered_begin = CALLBACK(self.__on_file_write_ordered_begin)
        if hasattr(self, "on_file_write_ordered_end"):
            self.cbacks.on_file_write_ordered_end = CALLBACK(self.__on_file_write_ordered_end)
        if hasattr(self, "on_file_get_type_extent"):
            self.cbacks.on_file_get_type_extent = CALLBACK(self.__on_file_get_type_extent)
        if hasattr(self, "on_register_datarep"):
            self.cbacks.on_register_datarep = CALLBACK(self.__on_register_datarep)
        if hasattr(self, "on_file_set_atomicity"):
            self.cbacks.on_file_set_atomicity = CALLBACK(self.__on_file_set_atomicity)
        if hasattr(self, "on_file_get_atomicity"):
            self.cbacks.on_file_get_atomicity = CALLBACK(self.__on_file_get_atomicity)
        if hasattr(self, "on_file_sync"):
            self.cbacks.on_file_sync = CALLBACK(self.__on_file_sync)
        if hasattr(self, "on_iotest"):
            self.cbacks.on_iotest = CALLBACK(self.__on_iotest)
        if hasattr(self, "on_iowait"):
            self.cbacks.on_iowait = CALLBACK(self.__on_iowait)
        if hasattr(self, "on_iotestall"):
            self.cbacks.on_iotestall = CALLBACK(self.__on_iotestall)
        if hasattr(self, "on_iowaitall"):
            self.cbacks.on_iowaitall = CALLBACK(self.__on_iowaitall)
        if hasattr(self, "on_iotestany"):
            self.cbacks.on_iotestany = CALLBACK(self.__on_iotestany)
        if hasattr(self, "on_iowaitany"):
            self.cbacks.on_iowaitany = CALLBACK(self.__on_iowaitany)
        if hasattr(self, "on_iowaitsome"):
            self.cbacks.on_iowaitsome = CALLBACK(self.__on_iowaitsome)
        if hasattr(self, "on_iotestsome"):
            self.cbacks.on_iotestsome = CALLBACK(self.__on_iotestsome)
        if hasattr(self, "on_function_enter"):
            self.cbacks.on_function_enter = CALLBACK(self.__on_function_enter)
        if hasattr(self, "on_function_exit"):
            self.cbacks.on_function_exit = CALLBACK(self.__on_function_exit)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *exc_details):
        self.close()

    def open(self):
        if self._profile:
            return

        # the weird conversions are for interfacing with c-strings
        file_name_buf = create_string_buffer(bytes(str(self.file_name), "utf-8"));

        # calling undumpi_read_datatype_sizes apparently moves the filepointer
        # to the end of the file, skipping everything - we therefore open the
        # file once to read the sizes, then reopen it again for real processing
        profile = undumpi_open(file_name_buf)
        sizes = DumpiSizeof()
        undumpi_read_datatype_sizes(profile, byref(sizes))
        self._type_sizes = [sizes.size[i] for i in range(sizes.count)]
        libc.free(sizes.size)
        undumpi_close(profile)

        # now open the file for real
        self._profile = undumpi_open(file_name_buf)

    def close(self):
        if self._profile:
            undumpi_close(self._profile)

    @property
    def type_sizes(self):
        if not self._profile:
            raise ValueError("Can't read data sizes without open dumpi trace.")
        return self._type_sizes

    def print_sizes(self):
        if not self._profile:
            raise ValueError("Can't read data sizes without open dumpi trace.")
        print("DataType Sizes:")
        for i, type_size in enumerate(self.type_sizes):
            if i < 28:
                print("  {0} has size {1}".format(DataType(i).name, type_size))
            else: # anything >= 28 is a user-defined type
                print("  user-defined-datatype has size {0}".format(type_size))
        print()

    def print_header(self):
        header = self.read_header()
        version = header.version
        timestamp = time.asctime(time.gmtime(header.starttime))
        meshdim = header.meshdim

        print("Header:")
        print("  version: {0}.{1}.{2}".format(version[0], version[1], version[2]))
        print("  starttime: {0}".format(timestamp))
        print("  hostname: {0}".format(header.hostname.decode('utf-8')))
        print("  username: {0}".format(header.username.decode('utf-8')))
        print("  meshdim: {0}".format(meshdim))
        print("  meshsize: [", end="")
        for i in range(meshdim):
            print("{0}".format(header.meshsize[i]), end="")
            if i < meshdim-1:
                print(", ", end="")
        print("]")
        print("  meshcrd: [", end="")
        for i in range(meshdim):
            print("{0}".format(header.meshcrd[i]), end="")
            if i < meshdim-1:
                print(", ", end="")
        print("]")
        print()

    def read_header(self):
        if not self._profile:
            raise ValueError("Can't read header without open dumpi trace.")
        return undumpi_read_header(self._profile).contents

    def print_footer(self):
        calls, _ = self.read_footer()
        print("Function Call Count:")
        for name, count in calls.items():
            print("  {0}: {1}".format(name, count))
        print()

    def read_footer(self):
        if not self._profile:
            raise ValueError("Can't read footer without open dumpi trace.")
        footer = undumpi_read_footer(self._profile).contents
        funcs = [(i, c) for i, c in enumerate(footer.call_count) if c > 0]
        ignored = [(i, c) for i, c in enumerate(footer.ignored_count) if c > 0]
        function_calls = {DumpiCallbacks._fields_[idx][0]: c for idx, c in funcs}
        ignored_calls = {DumpiCallbacks._fields_[idx][0]: c for idx, c in ignored}
        return function_calls, ignored_calls

    def print_keyvals(self):
        keyvals = self.read_keyvals()
        print("Total keyvals: {0}".format(len(keyvals)))
        for key, value in keyvals.items():
            print("  {0}={1}".format(key, value))

    def read_keyvals(self):
        if not self._profile:
            raise ValueError("Can't read keyvals without open dumpi trace.")
        record = undumpi_read_keyval_record(self._profile)
        keyvals = {}
        if record:
            current = record.contents.head
            while current:
                keyvals[current.contents.key] = current.contents.val
                current = current.contents.next
            libc.free(record)
        return keyvals

    def read_stream(self):
        if not self._profile:
            raise ValueError("Can't read stream without open dumpi trace.")
        undumpi_read_stream(self._profile, byref(self.cbacks), None)

    def __on_send(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiSend))
        try:
            self.on_send(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_recv(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiRecv))
        try:
            self.on_recv(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_get_count(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGetCount))
        try:
            self.on_get_count(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_bsend(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiBSend))
        try:
            self.on_bsend(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_ssend(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiSSend))
        try:
            self.on_ssend(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_rsend(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiRSend))
        try:
            self.on_rsend(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_buffer_attach(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiBufferAttach))
        try:
            self.on_buffer_attach(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_buffer_detach(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiBufferDetach))
        try:
            self.on_buffer_detach(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_isend(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiISend))
        try:
            self.on_isend(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_ibsend(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIbSend))
        try:
            self.on_ibsend(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_issend(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIsSend))
        try:
            self.on_issend(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_irsend(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIrSend))
        try:
            self.on_irsend(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_irecv(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIRecv))
        try:
            self.on_irecv(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_wait(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWait))
        try:
            self.on_wait(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_test(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTest))
        try:
            self.on_test(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_request_free(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiRequestFree))
        try:
            self.on_request_free(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_waitany(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWaitAny))
        try:
            self.on_waitany(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_testany(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTestAny))
        try:
            self.on_testany(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_waitall(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWaitAll))
        try:
            self.on_waitall(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_testall(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTestAll))
        try:
            self.on_testall(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_waitsome(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWaitSome))
        try:
            self.on_waitsome(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_testsome(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTestSome))
        try:
            self.on_testsome(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_iprobe(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIprobe))
        try:
            self.on_iprobe(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_probe(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiProbe))
        try:
            self.on_probe(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_cancel(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCancel))
        try:
            self.on_cancel(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_test_cancelled(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTestCancelled))
        try:
            self.on_test_cancelled(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_send_init(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiSendInit))
        try:
            self.on_send_init(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_bsend_init(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiBsendInit))
        try:
            self.on_bsend_init(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_ssend_init(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiSsendInit))
        try:
            self.on_ssend_init(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_rsend_init(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiRsendInit))
        try:
            self.on_rsend_init(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_recv_init(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiRecvInit))
        try:
            self.on_recv_init(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_start(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiStart))
        try:
            self.on_start(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_startall(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiStartall))
        try:
            self.on_startall(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_sendrecv(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiSendrecv))
        try:
            self.on_sendrecv(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_sendrecv_replace(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiSendrecvReplace))
        try:
            self.on_sendrecv_replace(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_contiguous(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeContiguous))
        try:
            self.on_type_contiguous(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_vector(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeVector))
        try:
            self.on_type_vector(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_hvector(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeHvector))
        try:
            self.on_type_hvector(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_indexed(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeIndexed))
        try:
            self.on_type_indexed(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_hindexed(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeHindexed))
        try:
            self.on_type_hindexed(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_struct(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeStruct))
        try:
            self.on_type_struct(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_address(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAddress))
        try:
            self.on_address(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_extent(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeExtent))
        try:
            self.on_type_extent(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_size(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeSize))
        try:
            self.on_type_size(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_lb(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeLb))
        try:
            self.on_type_lb(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_ub(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeUb))
        try:
            self.on_type_ub(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_commit(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeCommit))
        try:
            self.on_type_commit(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_free(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeFree))
        try:
            self.on_type_free(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_get_elements(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGetElements))
        try:
            self.on_get_elements(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_pack(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiPack))
        try:
            self.on_pack(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_unpack(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiUnpack))
        try:
            self.on_unpack(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_pack_size(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiPackSize))
        try:
            self.on_pack_size(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_barrier(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiBarrier))
        try:
            self.on_barrier(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_bcast(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiBcast))
        try:
            self.on_bcast(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_gather(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGather))
        try:
            self.on_gather(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_gatherv(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGatherv))
        try:
            self.on_gatherv(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_scatter(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiScatter))
        try:
            self.on_scatter(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_scatterv(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiScatterv))
        try:
            self.on_scatterv(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_allgather(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAllgather))
        try:
            self.on_allgather(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_allgatherv(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAllgatherv))
        try:
            self.on_allgatherv(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_alltoall(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAlltoall))
        try:
            self.on_alltoall(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_alltoallv(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAlltoallv))
        try:
            self.on_alltoallv(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_reduce(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiReduce))
        try:
            self.on_reduce(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_op_create(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiOpCreate))
        try:
            self.on_op_create(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_op_free(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiOpFree))
        try:
            self.on_op_free(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_allreduce(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAllreduce))
        try:
            self.on_allreduce(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_reduce_scatter(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiReduceScatter))
        try:
            self.on_reduce_scatter(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_scan(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiScan))
        try:
            self.on_scan(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_group_size(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGroupSize))
        try:
            self.on_group_size(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_group_rank(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGroupRank))
        try:
            self.on_group_rank(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_group_translate_ranks(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGroupTranslateRanks))
        try:
            self.on_group_translate_ranks(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_group_compare(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGroupCompare))
        try:
            self.on_group_compare(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_group(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommGroup))
        try:
            self.on_comm_group(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_group_union(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGroupUnion))
        try:
            self.on_group_union(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_group_intersection(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGroupIntersection))
        try:
            self.on_group_intersection(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_group_difference(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGroupDifference))
        try:
            self.on_group_difference(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_group_incl(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGroupIncl))
        try:
            self.on_group_incl(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_group_excl(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGroupExcl))
        try:
            self.on_group_excl(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_group_range_incl(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGroupRangeIncl))
        try:
            self.on_group_range_incl(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_group_range_excl(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGroupRangeExcl))
        try:
            self.on_group_range_excl(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_group_free(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGroupFree))
        try:
            self.on_group_free(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_size(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommSize))
        try:
            self.on_comm_size(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_rank(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommRank))
        try:
            self.on_comm_rank(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_compare(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommCompare))
        try:
            self.on_comm_compare(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_dup(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommDup))
        try:
            self.on_comm_dup(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_create(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommCreate))
        try:
            self.on_comm_create(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_split(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommSplit))
        try:
            self.on_comm_split(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_free(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommFree))
        try:
            self.on_comm_free(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_test_inter(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommTestInter))
        try:
            self.on_comm_test_inter(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_remote_size(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommRemoteSize))
        try:
            self.on_comm_remote_size(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_remote_group(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommRemoteGroup))
        try:
            self.on_comm_remote_group(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_intercomm_create(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIntercommCreate))
        try:
            self.on_intercomm_create(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_intercomm_merge(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIntercommMerge))
        try:
            self.on_intercomm_merge(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_keyval_create(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiKeyvalCreate))
        try:
            self.on_keyval_create(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_keyval_free(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiKeyvalFree))
        try:
            self.on_keyval_free(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_attr_put(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAttrPut))
        try:
            self.on_attr_put(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_attr_get(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAttrGet))
        try:
            self.on_attr_get(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_attr_delete(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAttrDelete))
        try:
            self.on_attr_delete(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_topo_test(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTopoTest))
        try:
            self.on_topo_test(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_cart_create(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCartCreate))
        try:
            self.on_cart_create(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_dims_create(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiDimsCreate))
        try:
            self.on_dims_create(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_graph_create(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGraphCreate))
        try:
            self.on_graph_create(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_graphdims_get(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGraphdimsGet))
        try:
            self.on_graphdims_get(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_graph_get(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGraphGet))
        try:
            self.on_graph_get(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_cartdim_get(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCartdimGet))
        try:
            self.on_cartdim_get(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_cart_get(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCartGet))
        try:
            self.on_cart_get(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_cart_rank(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCartRank))
        try:
            self.on_cart_rank(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_cart_coords(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCartCoords))
        try:
            self.on_cart_coords(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_graph_neighbors_count(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGraphNeighborsCount))
        try:
            self.on_graph_neighbors_count(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_graph_neighbors(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGraphNeighbors))
        try:
            self.on_graph_neighbors(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_cart_shift(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCartShift))
        try:
            self.on_cart_shift(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_cart_sub(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCartSub))
        try:
            self.on_cart_sub(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_cart_map(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCartMap))
        try:
            self.on_cart_map(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_graph_map(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGraphMap))
        try:
            self.on_graph_map(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_get_processor_name(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGetProcessorName))
        try:
            self.on_get_processor_name(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_get_version(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGetVersion))
        try:
            self.on_get_version(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_errhandler_create(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiErrhandlerCreate))
        try:
            self.on_errhandler_create(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_errhandler_set(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiErrhandlerSet))
        try:
            self.on_errhandler_set(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_errhandler_get(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiErrhandlerGet))
        try:
            self.on_errhandler_get(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_errhandler_free(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiErrhandlerFree))
        try:
            self.on_errhandler_free(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_error_string(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiErrorString))
        try:
            self.on_error_string(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_error_class(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiErrorClass))
        try:
            self.on_error_class(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_wtime(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWtime))
        try:
            self.on_wtime(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_wtick(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWtick))
        try:
            self.on_wtick(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_init(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiInit))
        try:
            self.on_init(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_finalize(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFinalize))
        try:
            self.on_finalize(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_initialized(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiInitialized))
        try:
            self.on_initialized(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_abort(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAbort))
        try:
            self.on_abort(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_close_port(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiClosePort))
        try:
            self.on_close_port(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_accept(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommAccept))
        try:
            self.on_comm_accept(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_connect(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommConnect))
        try:
            self.on_comm_connect(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_disconnect(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommDisconnect))
        try:
            self.on_comm_disconnect(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_get_parent(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommGetParent))
        try:
            self.on_comm_get_parent(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_join(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommJoin))
        try:
            self.on_comm_join(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_spawn(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommSpawn))
        try:
            self.on_comm_spawn(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_spawn_multiple(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommSpawnMultiple))
        try:
            self.on_comm_spawn_multiple(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_lookup_name(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiLookupName))
        try:
            self.on_lookup_name(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_open_port(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiOpenPort))
        try:
            self.on_open_port(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_publish_name(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiPublishName))
        try:
            self.on_publish_name(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_unpublish_name(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiUnpublishName))
        try:
            self.on_unpublish_name(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_accumulate(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAccumulate))
        try:
            self.on_accumulate(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_get(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGet))
        try:
            self.on_get(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_put(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiPut))
        try:
            self.on_put(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_complete(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinComplete))
        try:
            self.on_win_complete(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_create(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinCreate))
        try:
            self.on_win_create(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_fence(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinFence))
        try:
            self.on_win_fence(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_free(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinFree))
        try:
            self.on_win_free(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_get_group(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinGetGroup))
        try:
            self.on_win_get_group(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_lock(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinLock))
        try:
            self.on_win_lock(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_post(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinPost))
        try:
            self.on_win_post(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_start(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinStart))
        try:
            self.on_win_start(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_test(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinTest))
        try:
            self.on_win_test(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_unlock(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinUnlock))
        try:
            self.on_win_unlock(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_wait(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinWait))
        try:
            self.on_win_wait(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_alltoallw(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAlltoallw))
        try:
            self.on_alltoallw(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_exscan(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiExscan))
        try:
            self.on_exscan(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_add_error_class(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAddErrorClass))
        try:
            self.on_add_error_class(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_add_error_code(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAddErrorCode))
        try:
            self.on_add_error_code(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_add_error_string(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAddErrorString))
        try:
            self.on_add_error_string(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_call_errhandler(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommCallErrhandler))
        try:
            self.on_comm_call_errhandler(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_create_keyval(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommCreateKeyval))
        try:
            self.on_comm_create_keyval(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_delete_attr(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommDeleteAttr))
        try:
            self.on_comm_delete_attr(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_free_keyval(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommFreeKeyval))
        try:
            self.on_comm_free_keyval(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_get_attr(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommGetAttr))
        try:
            self.on_comm_get_attr(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_get_name(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommGetName))
        try:
            self.on_comm_get_name(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_set_attr(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommSetAttr))
        try:
            self.on_comm_set_attr(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_set_name(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommSetName))
        try:
            self.on_comm_set_name(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_call_errhandler(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileCallErrhandler))
        try:
            self.on_file_call_errhandler(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_grequest_complete(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGrequestComplete))
        try:
            self.on_grequest_complete(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_grequest_start(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGrequestStart))
        try:
            self.on_grequest_start(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_init_thread(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiInitThread))
        try:
            self.on_init_thread(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_is_thread_main(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIsThreadMain))
        try:
            self.on_is_thread_main(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_query_thread(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiQueryThread))
        try:
            self.on_query_thread(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_status_set_cancelled(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiStatusSetCancelled))
        try:
            self.on_status_set_cancelled(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_status_set_elements(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiStatusSetElements))
        try:
            self.on_status_set_elements(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_create_keyval(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeCreateKeyval))
        try:
            self.on_type_create_keyval(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_delete_attr(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeDeleteAttr))
        try:
            self.on_type_delete_attr(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_dup(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeDup))
        try:
            self.on_type_dup(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_free_keyval(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeFreeKeyval))
        try:
            self.on_type_free_keyval(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_get_attr(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeGetAttr))
        try:
            self.on_type_get_attr(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_get_contents(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeGetContents))
        try:
            self.on_type_get_contents(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_get_envelope(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeGetEnvelope))
        try:
            self.on_type_get_envelope(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_get_name(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeGetName))
        try:
            self.on_type_get_name(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_set_attr(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeSetAttr))
        try:
            self.on_type_set_attr(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_set_name(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeSetName))
        try:
            self.on_type_set_name(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_match_size(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeMatchSize))
        try:
            self.on_type_match_size(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_call_errhandler(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinCallErrhandler))
        try:
            self.on_win_call_errhandler(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_create_keyval(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinCreateKeyval))
        try:
            self.on_win_create_keyval(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_delete_attr(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinDeleteAttr))
        try:
            self.on_win_delete_attr(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_free_keyval(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinFreeKeyval))
        try:
            self.on_win_free_keyval(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_get_attr(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinGetAttr))
        try:
            self.on_win_get_attr(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_get_name(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinGetName))
        try:
            self.on_win_get_name(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_set_attr(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinSetAttr))
        try:
            self.on_win_set_attr(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_set_name(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinSetName))
        try:
            self.on_win_set_name(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_alloc_mem(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiAllocMem))
        try:
            self.on_alloc_mem(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_create_errhandler(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommCreateErrhandler))
        try:
            self.on_comm_create_errhandler(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_get_errhandler(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommGetErrhandler))
        try:
            self.on_comm_get_errhandler(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_comm_set_errhandler(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiCommSetErrhandler))
        try:
            self.on_comm_set_errhandler(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_create_errhandler(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileCreateErrhandler))
        try:
            self.on_file_create_errhandler(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_get_errhandler(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileGetErrhandler))
        try:
            self.on_file_get_errhandler(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_set_errhandler(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileSetErrhandler))
        try:
            self.on_file_set_errhandler(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_finalized(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFinalized))
        try:
            self.on_finalized(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_free_mem(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFreeMem))
        try:
            self.on_free_mem(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_get_address(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiGetAddress))
        try:
            self.on_get_address(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_info_create(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiInfoCreate))
        try:
            self.on_info_create(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_info_delete(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiInfoDelete))
        try:
            self.on_info_delete(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_info_dup(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiInfoDup))
        try:
            self.on_info_dup(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_info_free(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiInfoFree))
        try:
            self.on_info_free(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_info_get(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiInfoGet))
        try:
            self.on_info_get(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_info_get_nkeys(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiInfoGetNkeys))
        try:
            self.on_info_get_nkeys(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_info_get_nthkey(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiInfoGetNthkey))
        try:
            self.on_info_get_nthkey(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_info_get_valuelen(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiInfoGetValuelen))
        try:
            self.on_info_get_valuelen(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_info_set(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiInfoSet))
        try:
            self.on_info_set(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_pack_external(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiPackExternal))
        try:
            self.on_pack_external(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_pack_external_size(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiPackExternalSize))
        try:
            self.on_pack_external_size(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_request_get_status(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiRequestGetStatus))
        try:
            self.on_request_get_status(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_create_darray(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeCreateDarray))
        try:
            self.on_type_create_darray(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_create_hindexed(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeCreateHindexed))
        try:
            self.on_type_create_hindexed(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_create_hvector(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeCreateHvector))
        try:
            self.on_type_create_hvector(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_create_indexed_block(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeCreateIndexedBlock))
        try:
            self.on_type_create_indexed_block(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_create_resized(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeCreateResized))
        try:
            self.on_type_create_resized(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_create_struct(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeCreateStruct))
        try:
            self.on_type_create_struct(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_create_subarray(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeCreateSubarray))
        try:
            self.on_type_create_subarray(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_get_extent(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeGetExtent))
        try:
            self.on_type_get_extent(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_type_get_true_extent(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiTypeGetTrueExtent))
        try:
            self.on_type_get_true_extent(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_unpack_external(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiUnpackExternal))
        try:
            self.on_unpack_external(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_create_errhandler(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinCreateErrhandler))
        try:
            self.on_win_create_errhandler(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_get_errhandler(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinGetErrhandler))
        try:
            self.on_win_get_errhandler(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_win_set_errhandler(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiWinSetErrhandler))
        try:
            self.on_win_set_errhandler(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_open(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileOpen))
        try:
            self.on_file_open(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_close(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileClose))
        try:
            self.on_file_close(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_delete(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileDelete))
        try:
            self.on_file_delete(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_set_size(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileSetSize))
        try:
            self.on_file_set_size(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_preallocate(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFilePreallocate))
        try:
            self.on_file_preallocate(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_get_size(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileGetSize))
        try:
            self.on_file_get_size(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_get_group(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileGetGroup))
        try:
            self.on_file_get_group(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_get_amode(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileGetAmode))
        try:
            self.on_file_get_amode(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_set_info(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileSetInfo))
        try:
            self.on_file_set_info(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_get_info(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileGetInfo))
        try:
            self.on_file_get_info(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_set_view(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileSetView))
        try:
            self.on_file_set_view(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_get_view(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileGetView))
        try:
            self.on_file_get_view(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_read_at(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileReadAt))
        try:
            self.on_file_read_at(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_read_at_all(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileReadAtAll))
        try:
            self.on_file_read_at_all(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_write_at(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileWriteAt))
        try:
            self.on_file_write_at(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_write_at_all(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileWriteAtAll))
        try:
            self.on_file_write_at_all(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_iread_at(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileIreadAt))
        try:
            self.on_file_iread_at(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_iwrite_at(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileIwriteAt))
        try:
            self.on_file_iwrite_at(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_read(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileRead))
        try:
            self.on_file_read(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_read_all(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileReadAll))
        try:
            self.on_file_read_all(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_write(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileWrite))
        try:
            self.on_file_write(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_write_all(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileWriteAll))
        try:
            self.on_file_write_all(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_iread(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileIread))
        try:
            self.on_file_iread(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_iwrite(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileIwrite))
        try:
            self.on_file_iwrite(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_seek(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileSeek))
        try:
            self.on_file_seek(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_get_position(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileGetPosition))
        try:
            self.on_file_get_position(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_get_byte_offset(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileGetByteOffset))
        try:
            self.on_file_get_byte_offset(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_read_shared(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileReadShared))
        try:
            self.on_file_read_shared(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_write_shared(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileWriteShared))
        try:
            self.on_file_write_shared(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_iread_shared(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileIreadShared))
        try:
            self.on_file_iread_shared(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_iwrite_shared(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileIwriteShared))
        try:
            self.on_file_iwrite_shared(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_read_ordered(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileReadOrdered))
        try:
            self.on_file_read_ordered(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_write_ordered(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileWriteOrdered))
        try:
            self.on_file_write_ordered(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_seek_shared(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileSeekShared))
        try:
            self.on_file_seek_shared(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_get_position_shared(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileGetPositionShared))
        try:
            self.on_file_get_position_shared(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_read_at_all_begin(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileReadAtAllBegin))
        try:
            self.on_file_read_at_all_begin(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_read_at_all_end(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileReadAtAllEnd))
        try:
            self.on_file_read_at_all_end(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_write_at_all_begin(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileWriteAtAllBegin))
        try:
            self.on_file_write_at_all_begin(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_write_at_all_end(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileWriteAtAllEnd))
        try:
            self.on_file_write_at_all_end(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_read_all_begin(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileReadAllBegin))
        try:
            self.on_file_read_all_begin(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_read_all_end(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileReadAllEnd))
        try:
            self.on_file_read_all_end(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_write_all_begin(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileWriteAllBegin))
        try:
            self.on_file_write_all_begin(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_write_all_end(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileWriteAllEnd))
        try:
            self.on_file_write_all_end(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_read_ordered_begin(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileReadOrderedBegin))
        try:
            self.on_file_read_ordered_begin(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_read_ordered_end(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileReadOrderedEnd))
        try:
            self.on_file_read_ordered_end(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_write_ordered_begin(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileWriteOrderedBegin))
        try:
            self.on_file_write_ordered_begin(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_write_ordered_end(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileWriteOrderedEnd))
        try:
            self.on_file_write_ordered_end(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_get_type_extent(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileGetTypeExtent))
        try:
            self.on_file_get_type_extent(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_register_datarep(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiRegisterDatarep))
        try:
            self.on_register_datarep(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_set_atomicity(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileSetAtomicity))
        try:
            self.on_file_set_atomicity(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_get_atomicity(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileGetAtomicity))
        try:
            self.on_file_get_atomicity(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_file_sync(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFileSync))
        try:
            self.on_file_sync(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_iotest(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIotest))
        try:
            self.on_iotest(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_iowait(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIowait))
        try:
            self.on_iowait(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_iotestall(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIotestall))
        try:
            self.on_iotestall(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_iowaitall(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIowaitall))
        try:
            self.on_iowaitall(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_iotestany(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIotestany))
        try:
            self.on_iotestany(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_iowaitany(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIowaitany))
        try:
            self.on_iowaitany(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_iowaitsome(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIowaitsome))
        try:
            self.on_iowaitsome(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_iotestsome(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiIotestsome))
        try:
            self.on_iotestsome(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_function_enter(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFuncCall))
        try:
            self.on_function_enter(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1

    def __on_function_exit(self, data, thread, cpu_time, wall_time, perf_info, userdata):
        dp = cast(data, POINTER(DumpiFuncCall))
        try:
            self.on_function_exit(dp.contents, thread, cpu_time.contents, wall_time.contents, perf_info.contents)
        except:
            traceback.print_exc()
            sys.exit(1)
        return 1
