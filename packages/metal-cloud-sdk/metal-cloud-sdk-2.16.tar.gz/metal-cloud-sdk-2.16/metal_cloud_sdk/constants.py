import inspect
import json
import importlib

class Constants(object):

	"""
	* Metal Cloud, API v2.16
	"""
	
	
	"""
	SaaS cluster of type Cloudera.
	
	See http://www.cloudera.com/ for more information on this software.
	"""
	CLUSTER_TYPE_CLOUDERA="cloudera"
	
	
	"""
	SaaS cluster of type Couchbase.
	
	See http://www.couchbase.com/ for information on this software.
	"""
	CLUSTER_TYPE_COUCHBASE="couchbase"
	
	
	"""
	SaaS cluster of type Datameer.
	
	See http://www.datameer.com/ for information on this software.
	"""
	CLUSTER_TYPE_DATAMEER="datameer"
	
	
	"""
	Datastax cluster type.
	
	
	"""
	CLUSTER_TYPE_DATASTAX="datastax"
	
	
	"""
	SaaS cluster of type ElasticSearch.
	
	See http://www.elasticsearch.org/ for more information on this software.
	"""
	CLUSTER_TYPE_ELASTICSEARCH="elasticsearch"
	
	
	"""
	SaaS cluster of type ElasticSearch.
	
	See http://www.elasticsearch.org/ for more information on this software.
	"""
	CLUSTER_TYPE_ELASTICSEARCH_LEGACY="elasticsearch_legacy"
	
	
	"""
	Exasol cluster type.
	
	
	"""
	CLUSTER_TYPE_EXASOL="exasol"
	
	
	"""
	HDFS Cluster.
	
	
	"""
	CLUSTER_TYPE_HDFS="hdfs"
	
	
	"""
	SaaS cluster of type Hortonworks.
	
	SaaS cluster of type MapR
	"""
	CLUSTER_TYPE_HORTONWORKS="hortonworks"
	
	
	"""
	SaaS cluster of type MapR.
	
	SaaS cluster of type MapR
	"""
	CLUSTER_TYPE_MAPR="mapr"
	
	
	"""
	SaaS cluster of type MapRLegacy.
	
	SaaS cluster of type MapRLegacy
	"""
	CLUSTER_TYPE_MAPR_LEGACY="mapr_legacy"
	
	
	"""
	Mesos cluster type.
	
	
	"""
	CLUSTER_TYPE_MESOS="mesos"
	
	
	"""
	Percona MySQL cluster.
	
	See https://www.percona.com/software/mysql-database/percona-xtradb-cluster for information on this software.
	"""
	CLUSTER_TYPE_MYSQL_PERCONA="mysql_percona"
	
	
	"""
	SaaS cluster of type Splunk.
	
	See http://www.splunk.com/ for information on this software.
	"""
	CLUSTER_TYPE_SPLUNK="splunk"
	
	
	"""
	SaaS cluster of type Tableau.
	
	See http://www.tableau.com/ for information on this software.
	
	"""
	CLUSTER_TYPE_TABLEAU="tableau"
	
	
	"""
	Vanilla cluster type (blank).
	
	Default cluster, with blank behaviour (does nothing special and installs no special [SaaS] software). It is a singleton per Infrastructure product.
	"""
	CLUSTER_TYPE_VANILLA="vanilla"
	
	
	"""
	SQLSelection array row span.
	
	
	"""
	COLLAPSE_ARRAY_ROW_SPAN="array_row_span"
	
	
	"""
	SQLSelection array subrows.
	
	
	"""
	COLLAPSE_ARRAY_SUBROWS="array_subrows"
	
	
	"""
	SQLSelection array subrows table.
	
	
	"""
	COLLAPSE_ARRAY_SUBROWS_TABLE="array_subrows_table"
	
	
	"""
	SQLSelection autocomplete dictionary.
	
	
	"""
	COLLAPSE_AUTOCOMPLETE_DICTIONARY="autocomplete_dictionary"
	
	
	"""
	SQLSelection HTML rows array.
	
	
	"""
	COLLAPSE_HTML_ROWS_ARRAY="html_rows_array"
	
	
	"""
	SQLSelection HTML rows string.
	
	
	"""
	COLLAPSE_HTML_ROWS_STRING="html_rows_string"
	
	
	"""
	SQLSelection none.
	
	
	"""
	COLLAPSE_NONE="none"
	
	
	"""
	ContainerArray execute command action.
	
	ContainerArray action that executes a given command.
	"""
	CONTAINER_ARRAY_ACTION_EXECUTE_COMMAND="execute_command"
	
	
	"""
	ContainerArray HTTP get action.
	
	ContainerArray action that makes a HTTP get request.
	"""
	CONTAINER_ARRAY_ACTION_HTTP_GET="http_get"
	
	
	"""
	ContainerArray TCP socket action.
	
	ContainerArray action that opens a TCP connection to a given port.
	"""
	CONTAINER_ARRAY_ACTION_TCP_SOCKET="tcp_socket"
	
	
	"""
	SAN ContainerArray interface.
	
	ContainerArray interface index reserved for SAN networks.
	"""
	CONTAINER_ARRAY_INTERFACE_INDEX_0=0
	
	
	"""
	ContainerArray interface index 1.
	
	
	"""
	CONTAINER_ARRAY_INTERFACE_INDEX_1=1
	
	
	"""
	ContainerArray interface index 2.
	
	
	"""
	CONTAINER_ARRAY_INTERFACE_INDEX_2=2
	
	
	"""
	Elasticsearch container cluster type.
	
	
	"""
	CONTAINER_CLUSTER_TYPE_ELASTICSEARCH="elasticsearch"
	
	
	"""
	Kafka container cluster type.
	
	
	"""
	CONTAINER_CLUSTER_TYPE_KAFKA="kafka"
	
	
	"""
	PostgreSQL container cluster type.
	
	
	"""
	CONTAINER_CLUSTER_TYPE_POSTGRESQL="postgresql"
	
	
	"""
	Spark container cluster type.
	
	
	"""
	CONTAINER_CLUSTER_TYPE_SPARK="spark"
	
	
	"""
	SparkSQL container cluster type.
	
	
	"""
	CONTAINER_CLUSTER_TYPE_SPARKSQL="sparksql"
	
	
	"""
	StreamSets container cluster type.
	
	StreamSets container cluster type
	"""
	CONTAINER_CLUSTER_TYPE_STREAMSETS="streamsets"
	
	
	"""
	Vanilla container cluster type.
	
	Default container cluster, with blank behaviour. It is a singleton per ContainerPlatform product.
	"""
	CONTAINER_CLUSTER_TYPE_VANILLA="vanilla"
	
	
	"""
	Zookeeper container cluster type.
	
	
	"""
	CONTAINER_CLUSTER_TYPE_ZOOKEEPER="zookeeper"
	
	
	"""
	Zoomdata container cluster type.
	
	
	"""
	CONTAINER_CLUSTER_TYPE_ZOOMDATA="zoomdata"
	
	
	"""
	Container failed phase.
	
	The Container has failed.
	"""
	CONTAINER_STATUS_PHASE_FAILED="failed"
	
	
	"""
	Container pending phase.
	
	The Container has been created and awaits scheduling and execution.
	"""
	CONTAINER_STATUS_PHASE_PENDING="pending"
	
	
	"""
	Container running phase.
	
	Container is running.
	"""
	CONTAINER_STATUS_PHASE_RUNNING="running"
	
	
	"""
	Container succeeded phase.
	
	The Container has been executed successfully.
	"""
	CONTAINER_STATUS_PHASE_SUCCEEDED="succeeded"
	
	
	"""
	Container unknown phase.
	
	The Container state phase could not be retrieved due to internal errors.
	"""
	CONTAINER_STATUS_PHASE_UNKNOWN="unknown"
	
	
	"""
	HDFS DataLake type.
	
	
	"""
	DATA_LAKE_TYPE_HDFS="hdfs"
	
	
	"""
	Disk Type HDD.
	
	Type of server local disk
	"""
	DISK_TYPE_HDD="HDD"
	
	
	"""
	Disk Type none.
	
	Server local disk type
	"""
	DISK_TYPE_NONE="none"
	
	
	"""
	Disk Type NVME.
	
	Type of server local disk
	"""
	DISK_TYPE_NVME="NVME"
	
	
	"""
	Disk Type SSD.
	
	Type of server local disk
	"""
	DISK_TYPE_SSD="SSD"
	
	
	"""
	HDD drive.
	
	
	"""
	DRIVE_STORAGE_TYPE_ISCSI_HDD="iscsi_hdd"
	
	
	"""
	SSD drive.
	
	
	"""
	DRIVE_STORAGE_TYPE_ISCSI_SSD="iscsi_ssd"
	
	
	"""
	Important event.
	
	
	"""
	EVENT_SEVERITY_IMPORTANT="important"
	
	
	"""
	Info event.
	
	
	"""
	EVENT_SEVERITY_INFO="info"
	
	
	"""
	Security event.
	
	Events such as log-in, log out, password changes, account recovery, authenticator added or removed, etc.
	"""
	EVENT_SEVERITY_SECURITY="security"
	
	
	"""
	Success event.
	
	
	"""
	EVENT_SEVERITY_SUCCESS="success"
	
	
	"""
	Trigger event.
	
	
	"""
	EVENT_SEVERITY_TRIGGER="trigger"
	
	
	"""
	Warning event.
	
	
	"""
	EVENT_SEVERITY_WARNING="warning"
	
	
	"""
	Filesystem navigator driver dataset readme.
	
	
	"""
	FILESYSTEM_NAVIGATOR_DRIVER_TYPE_DATASET_README="dataset_readme"
	
	
	"""
	FileSystemNavigator driver of type WebHDFS.
	
	
	"""
	FILESYSTEM_NAVIGATOR_DRIVER_TYPE_WEBHDFS="webhdfs"
	
	
	"""
	FirewallRule IPV4.
	
	
	"""
	FIREWALL_RULE_IP_ADDRESS_TYPE_IPV4="ipv4"
	
	
	"""
	FirewallRule IPV6.
	
	
	"""
	FIREWALL_RULE_IP_ADDRESS_TYPE_IPV6="ipv6"
	
	
	"""
	FirewallRule Protocol All.
	
	
	"""
	FIREWALL_RULE_PROTOCOL_ALL="all"
	
	
	"""
	FirewallRule Protocol ICMP.
	
	
	"""
	FIREWALL_RULE_PROTOCOL_ICMP="icmp"
	
	
	"""
	FirewallRule Protocol TCP.
	
	
	"""
	FIREWALL_RULE_PROTOCOL_TCP="tcp"
	
	
	"""
	FirewallRule Protocol UDP.
	
	
	"""
	FIREWALL_RULE_PROTOCOL_UDP="udp"
	
	
	"""
	Guest.
	
	
	"""
	GUEST_DISPLAY_NAME="Guest"
	
	
	"""
	Predefined hardware configurations.
	
	
	"""
	HARDWARE_CONFIGURATIONS_PREDEFINED="predefined"
	
	
	"""
	User predefined hardware configurations.
	
	
	"""
	HARDWARE_CONFIGURATIONS_USER_PREDEFINED="user_predefined"
	
	
	"""
	Instance array boot method local drives.
	
	Instance array boot method local drives
	"""
	INSTANCE_ARRAY_BOOT_METHOD_LOCAL_DRIVES="local_drives"
	
	
	"""
	Instance array boot method PXE ISCSI.
	
	Instance array boot method PXE ISCSI
	"""
	INSTANCE_ARRAY_BOOT_METHOD_PXE_ISCSI="pxe_iscsi"
	
	
	"""
	SAN InstanceArray interface.
	
	InstanceArray interface index reserved for SAN networks.
	"""
	INSTANCE_ARRAY_INTERFACE_INDEX_0=0
	
	
	"""
	InstanceArray interface index 1.
	
	
	"""
	INSTANCE_ARRAY_INTERFACE_INDEX_1=1
	
	
	"""
	InstanceArray interface index 2.
	
	
	"""
	INSTANCE_ARRAY_INTERFACE_INDEX_2=2
	
	
	"""
	InstanceArray interface index 3.
	
	
	"""
	INSTANCE_ARRAY_INTERFACE_INDEX_3=3
	
	
	"""
	Microsoft minimum number of processors for two core license pack.
	
	
	"""
	LICENSE_MICROSOFT_PROCESSOR_MIN_COUNT=8
	
	
	"""
	License Type None.
	
	
	"""
	LICENSE_TYPE_NONE="none"
	
	
	"""
	License type windows server.
	
	
	"""
	LICENSE_TYPE_WINDOWS_SERVER="windows_server"
	
	
	"""
	License type Windows Server Standard.
	
	
	"""
	LICENSE_TYPE_WINDOWS_SERVER_STANDARD="windows_server_standard"
	
	
	"""
	Demand license utilization.
	
	
	"""
	LICENSE_UTILIZATION_TYPE_DEMAND="demand"
	
	
	"""
	License Utilization Type None.
	
	
	"""
	LICENSE_UTILIZATION_TYPE_NONE="none"
	
	
	"""
	Subscribe license utilization.
	
	
	"""
	LICENSE_UTILIZATION_TYPE_SUBSCRIPTION="subscription"
	
	
	"""
	SaaS LAN Network.
	
	SaaS flag for LAN network 
	"""
	NETWORK_CUSTOM_TYPE_SAAS="saas"
	
	
	"""
	Network suspend status not suspended.
	
	
	"""
	NETWORK_SUSPEND_STATUS_NOT_SUSPENDED="not_suspended"
	
	
	"""
	Network suspend status suspended.
	
	
	"""
	NETWORK_SUSPEND_STATUS_SUSPENDED="suspended"
	
	
	"""
	Network suspend status suspending.
	
	
	"""
	NETWORK_SUSPEND_STATUS_SUSPENDING="suspending"
	
	
	"""
	Network suspend status unsuspending.
	
	
	"""
	NETWORK_SUSPEND_STATUS_UNSUSPENDING="unsuspending"
	
	
	"""
	LAN network.
	
	
	"""
	NETWORK_TYPE_LAN="lan"
	
	
	"""
	SAN network.
	
	
	"""
	NETWORK_TYPE_SAN="san"
	
	
	"""
	WAN network.
	
	
	"""
	NETWORK_TYPE_WAN="wan"
	
	
	"""
	CPU Load node measurement type.
	
	
	"""
	NODE_MEASUREMENT_TYPE_CPU_LOAD="cpu_load"
	
	
	"""
	Disk size node measurement type.
	
	
	"""
	NODE_MEASUREMENT_TYPE_DISK_SIZE="disk_size"
	
	
	"""
	Disk used node measurement type.
	
	
	"""
	NODE_MEASUREMENT_TYPE_DISK_USED="disk_used"
	
	
	"""
	Network interface input node measurement type.
	
	
	"""
	NODE_MEASUREMENT_TYPE_NETWORK_INTERFACE_INPUT="net_if_input"
	
	
	"""
	Network interface output node measurement type.
	
	
	"""
	NODE_MEASUREMENT_TYPE_NETWORK_INTERFACE_OUTPUT="net_if_output"
	
	
	"""
	RAM size node measurement type.
	
	
	"""
	NODE_MEASUREMENT_TYPE_RAM_SIZE="ram_size"
	
	
	"""
	RAM used node measurement type.
	
	
	"""
	NODE_MEASUREMENT_TYPE_RAM_USED="ram_used"
	
	
	"""
	Operating System Centos.
	
	
	"""
	OPERATING_SYSTEM_CENTOS="CentOS"
	
	
	"""
	Operating System None.
	
	
	"""
	OPERATING_SYSTEM_NONE="none"
	
	
	"""
	Operating System Ubuntu.
	
	
	"""
	OPERATING_SYSTEM_UBUNTU="Ubuntu"
	
	
	"""
	Operating System Windows.
	
	
	"""
	OPERATING_SYSTEM_WINDOWS="Windows"
	
	
	"""
	Create operation.
	
	
	"""
	OPERATION_TYPE_CREATE="create"
	
	
	"""
	Delete operation.
	
	
	"""
	OPERATION_TYPE_DELETE="delete"
	
	
	"""
	Edit operation.
	
	
	"""
	OPERATION_TYPE_EDIT="edit"
	
	
	"""
	Start operation.
	
	
	"""
	OPERATION_TYPE_START="start"
	
	
	"""
	Stop operation.
	
	
	"""
	OPERATION_TYPE_STOP="stop"
	
	
	"""
	Suspend operation.
	
	
	"""
	OPERATION_TYPE_SUSPEND="suspend"
	
	
	"""
	Prices key for private datacenters default prices.
	
	
	"""
	PRICES_PRIVATE_DATACENTER_KEY="private-dc-default"
	
	
	"""
	Finished provision status.
	
	
	"""
	PROVISION_STATUS_FINISHED="finished"
	
	
	"""
	Not started provision status.
	
	
	"""
	PROVISION_STATUS_NOT_STARTED="not_started"
	
	
	"""
	Ongoing provision status.
	
	
	"""
	PROVISION_STATUS_ONGOING="ongoing"
	
	
	"""
	Redis critical token.
	
	Redis critical token
	"""
	REDIS_CRITICAL_TOKEN="critical"
	
	
	"""
	Invalid redis token.
	
	
	"""
	REDIS_INVALID_TOKEN="invalid"
	
	
	"""
	Redis token.
	
	
	"""
	REDIS_TOKEN="token"
	
	
	"""
	Valid redis token.
	
	
	"""
	REDIS_VALID_TOKEN="valid"
	
	
	"""
	Active reservation installment.
	
	
	"""
	RESERVATION_INSTALLMENT_STATUS_ACTIVE="active"
	
	
	"""
	Stopped reservation installment.
	
	
	"""
	RESERVATION_INSTALLMENT_STATUS_STOPPED="stopped"
	
	
	"""
	Active reservation.
	
	
	"""
	RESERVATION_STATUS_ACTIVE="active"
	
	
	"""
	Stopped reservation.
	
	
	"""
	RESERVATION_STATUS_STOPPED="stopped"
	
	
	"""
	Subnet resource reservation.
	
	
	"""
	RESERVATION_SUBNET="subnet"
	
	
	"""
	Demand resource utilization.
	
	
	"""
	RESOURCE_UTILIZATION_TYPE_DEMAND="demand"
	
	
	"""
	Reserve resource utilization.
	
	
	"""
	RESOURCE_UTILIZATION_TYPE_RESERVATION="reservation"
	
	
	"""
	Big data server class.
	
	Very general workload type designation.
	"""
	SERVER_CLASS_BIGDATA="bigdata"
	
	
	"""
	HDFS server class.
	
	Very general workload type designation.
	"""
	SERVER_CLASS_HDFS="hdfs"
	
	
	"""
	Unknown server class.
	
	Very general workload type designation. Unknown class servers cannot be used.
	"""
	SERVER_CLASS_UNKNOWN="unknown"
	
	
	"""
	Null power command. No action.
	
	Used with some power functions which are both setter and getter to just interrogate without action.
	"""
	SERVER_POWER_STATUS_NONE="none"
	
	
	"""
	Server powered off.
	
	Power down chassis into soft off (S4/S5 state). WARNING: This command does not initiate a clean shutdown of the operating system prior to powering down the system.
	"""
	SERVER_POWER_STATUS_OFF="off"
	
	
	"""
	Server powered on.
	
	Power up chassis.
	"""
	SERVER_POWER_STATUS_ON="on"
	
	
	"""
	Server power reset.
	
	This command will perform a hard reset.
	"""
	SERVER_POWER_STATUS_RESET="reset"
	
	
	"""
	Server power status soft.
	
	Initiate a soft-shutdown of OS via ACPI. This can be done in a number of ways, commonly by simulating an overtemperture or by simulating a power button press. It is necessary for there to be Operating System support for ACPI and some sort of daemon watching for events for this soft power to work.
	"""
	SERVER_POWER_STATUS_SOFT="soft"
	
	
	"""
	Server power status unknown.
	
	Returned when a server is not allocated to an instance, the instance is not deployed or has an ongoing deploy operation.
	"""
	SERVER_POWER_STATUS_UNKNOWN="unknown"
	
	
	"""
	Active service status.
	
	
	"""
	SERVICE_STATUS_ACTIVE="active"
	
	
	"""
	Deleted service status.
	
	
	"""
	SERVICE_STATUS_DELETED="deleted"
	
	
	"""
	Ordered service status.
	
	
	"""
	SERVICE_STATUS_ORDERED="ordered"
	
	
	"""
	Stopped service status.
	
	
	"""
	SERVICE_STATUS_STOPPED="stopped"
	
	
	"""
	Suspended service status.
	
	
	"""
	SERVICE_STATUS_SUSPENDED="suspended"
	
	
	"""
	Shared drive - connection type "connected".
	
	When an instance array or a container array is attached to a shared drive and the infrastructure is deployed, this kind of connection will be made.
	"""
	SHARED_DRIVE_CONNECTED="connected"
	
	
	"""
	Shared drive - connection type "connected".
	
	
	"""
	SHARED_DRIVE_CONNECTED_CONTAINER_ARRAY="connected_container_array"
	
	
	"""
	Shared drive - connection type "disconnected".
	
	
	"""
	SHARED_DRIVE_DISCONNECTED_CONTAINER_ARRAY="disconnected_container_array"
	
	
	"""
	Shared drive connection type "will be connected".
	
	When an instance array or a container array is attached to a shared drive, this type of connection will be made.
	"""
	SHARED_DRIVE_WILL_BE_CONNECTED="will_be_connected"
	
	
	"""
	Shared drive connection type "will be connected".
	
	
	"""
	SHARED_DRIVE_WILL_BE_CONNECTED_CONTAINER_ARRAY="will_be_connected_container_array"
	
	
	"""
	Shared drive - connection type "will_be_disconnected".
	
	When an instance array / container array is detached from a shared drive (or the shared drive / instance array / container array belonging to the connection is deleted), this type of connection will be made.
	"""
	SHARED_DRIVE_WILL_BE_DISCONNECTED="will_be_disconnected"
	
	
	"""
	Shared drive - connection type "will_be_disconnected".
	
	
	"""
	SHARED_DRIVE_WILL_BE_DISCONNECTED_CONTAINER_ARRAY="will_be_disconnected_container_array"
	
	
	"""
	Solution of type Datalab Spark.
	
	
	"""
	SOLUTION_TYPE_DATALAB_SPARK="datalab_spark"
	
	
	"""
	DSA algorithm.
	
	
	"""
	SSH_DSA_ALGORITHM_IDENTIFIER="ssh-dsa"
	
	
	"""
	DSS algorithm.
	
	
	"""
	SSH_DSS_ALGORITHM_IDENTIFIER="ssh-dss"
	
	
	"""
	OpenSSH SSH key.
	
	
	"""
	SSH_KEY_FORMAT_OPENSSH="openssh"
	
	
	"""
	PKCS1 SSH key.
	
	
	"""
	SSH_KEY_FORMAT_PKCS1="pkcs#1"
	
	
	"""
	PKCS8 SSH key.
	
	
	"""
	SSH_KEY_FORMAT_PKCS8="pkcs#8"
	
	
	"""
	SSH2 SSH key.
	
	
	"""
	SSH_KEY_FORMAT_SSH2="ssh2"
	
	
	"""
	RSA algorithm.
	
	
	"""
	SSH_RSA_ALGORITHM_IDENTIFIER="ssh-rsa"
	
	
	"""
	LAN Subnet.
	
	
	"""
	SUBNET_DESTINATION_LAN="lan"
	
	
	"""
	SAN Subnet.
	
	
	"""
	SUBNET_DESTINATION_SAN="san"
	
	
	"""
	WAN Subnet.
	
	
	"""
	SUBNET_DESTINATION_WAN="wan"
	
	
	"""
	IPv4 Subnet.
	
	
	"""
	SUBNET_TYPE_IPV4="ipv4"
	
	
	"""
	IPv6 Subnet.
	
	
	"""
	SUBNET_TYPE_IPV6="ipv6"
	
	
	"""
	URL Type HDFS.
	
	
	"""
	URL_TYPE_HDFS="hdfs"
	
	
	"""
	User access level - customer.
	
	
	"""
	USER_ACCESS_LEVEL_CUSTOMER="customer"
	
	
	"""
	Not verified user e-mail address.
	
	
	"""
	USER_LOGIN_EMAIL_STATUS_NOT_VERIFIED="not_verified"
	
	
	"""
	Verified user e-mail address.
	
	
	"""
	USER_LOGIN_EMAIL_STATUS_VERIFIED="verified"
	
	
	"""
	User Plan Type Custom.
	
	
	"""
	USER_PLAN_TYPE_CUSTOM="custom"
	
	
	"""
	User Plan Type Starter.
	
	
	"""
	USER_PLAN_TYPE_STARTER="starter"
	
	
	"""
	User Plan Type Starter Redundant.
	
	
	"""
	USER_PLAN_TYPE_STARTER_REDUNDANT="starter_redundant"
	
	
	"""
	User Plan Type Vanilla.
	
	
	"""
	USER_PLAN_TYPE_VANILLA="vanilla"
	
	
	"""
	Active user SSH key.
	
	
	"""
	USER_SSH_KEY_STATUS_ACTIVE="active"
	
	
	"""
	Deleted user SSH key.
	
	
	"""
	USER_SSH_KEY_STATUS_DELETED="deleted"
	
	
	"""
	User suspend reason custom.
	
	
	"""
	USER_SUSPEND_REASON_CUSTOM="custom"
	
	
	"""
	User suspend reason unpaid.
	
	
	"""
	USER_SUSPEND_REASON_UNPAID="unpaid"
	
	
	"""
	Admin user.
	
	
	"""
	USER_TYPE_ADMIN="admin"
	
	
	"""
	Billable user.
	
	
	"""
	USER_TYPE_BILLABLE="billable"
	
	
	"""
	Volume template deprecation status deprecated allow expand.
	
	Volume template deprecation status deprecated allow expand
	"""
	VOLUME_TEMPLATE_DEPRECATION_STATUS_DEPRECATED_ALLOW_EXPAND="deprecated_allow_expand"
	
	
	"""
	Volume template deprecation status deprecated deny provision.
	
	Volume template deprecation status deprecated deny provision
	"""
	VOLUME_TEMPLATE_DEPRECATION_STATUS_DEPRECATED_DENY_PROVISION="deprecated_deny_provision"
	
	
	"""
	Volume template deprecation status not deprecated.
	
	Volume template deprecation status not deprecated
	"""
	VOLUME_TEMPLATE_DEPRECATION_STATUS_NOT_DEPRECATED="not_deprecated"
	
	
	"""
	Active status volume template.
	
	
	"""
	VOLUME_TEMPLATE_STATUS_ACTIVE="active"
	
	
	"""
	Deleted status volume template.
	
	
	"""
	VOLUME_TEMPLATE_STATUS_DELETED="deleted"
	