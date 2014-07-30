####################################
### @file tc-utils.tcl
###
### @brief routine utilities for tcl client
###
### @author hum, fangq, mingyr (@sugon.com)
### @date 2013-03-15
###
### @note tc abbreviates for tcl client
####################################


####################################
# @note implemented Protocol:
# +-----------+-----------------+--------------+
# |   Name    |       Aim       |    Return    |
# +-----------+-----------------+--------------+
# | test_echo | activity check  |  hello msg   |
# +-----------+-----------------+--------------+
# | test_exec |    RPC calls    |  exec result |
# +-----------+-----------------+--------------+
####################################

### Package from tcllib
package require comm;

###@brief Initializing tcl client
###@param port Port parameter of server address
###@param server IP parameter of server address
###@return Return of value of TCL type list,
###first elem denote return code, 0 for success and
###-1 for failure; second elem depicts the reason
###@note Server activity is checked against continuous processing
proc tc_init {port {server localhost}} {
    
    if {![regexp {(^[0-9a-fA-F:\.]+$)|(localhost)} $server]} {
        return [list -1 "Invalid server address"]
    }
    
    if [catch {expr $port} err] {
        return [list -1 "Invalid server port: $err"]
    }

    if {[catch {set res [comm::comm send [list $port $server] test_echo]} err]} {
        return [list -1 $err]
    } else {
        switch -regexp -- $res {
            {^\-\d+\s*\w*} {
                return [list -1 [string range $res 3 end]]
            }
            {^\d+\s*\w*} {
                set s [string trim [string range $res 2 end]]
                if [regexp {^\d+$} $s] {
                        return [list 0 $s]
                } else {
                        return [list -1 "Invalid handshake message"]
                }
            }
        }
    }
}

###@brief Execute the pseudo RPC
###@param args Arguments of varying length
###must of the form [server_port server_ip RPC_Name RPC_param RPC_param2 ... RPC_paramN]
###@return Same meaning as tc_init. However RPC return
###will be reflected honstly
proc tc_exec {args} {
    if {[llength $args] <= 2} {
        return [list -1 "Insufficient arguments"]
    }
    
    set params [lrange $args 2 [expr [llength $args] - 1]]
    
    if {[catch {set res [comm::comm send [list [lindex $args 0] [lindex $args 1]] test_exec $params]} err]} {
        return [list -1 "Error when executing command"]
    } else {
        switch -regexp -- $res {
            {^\-\d+\s*\w*} {
                return [list -1 [string range $res 3 end]]
            }
            {^\d+\s*\w*} {
                return [list 0 [string range $res 2 end]]
            }
        }
    }
}

###@brief Trivial exit
proc tc_exit {} {
    return [list 0 ""]
}
