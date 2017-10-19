#include <stdio.h>
#include <stdlib.h>
#include <xmlrpc-c/client.h>

#define NAME       "XML-RPC getSumAndDifference C Client"
#define VERSION    "0.1"
#define SERVER_URL "http://xmlrpc-c.sourceforge.net/api/sample.php"

void die_if_fault_occurred (xmlrpc_env *env)
{
    /* Check our error-handling environment for an XML-RPC fault. */
    if (env->fault_occurred) {
        fprintf(stderr, "XML-RPC Fault: %s (%d)\n",
                env->fault_string, env->fault_code);
        exit(1);
    }
}

int main (int argc, char** argv)
{
    xmlrpc_env env;
    xmlrpc_value *result;
    xmlrpc_int32 sum, difference;
    
    /* Start up our XML-RPC client library. */
    xmlrpc_client_init(XMLRPC_CLIENT_NO_FLAGS, NAME, VERSION);
    xmlrpc_env_init(&env);

    /* Call our XML-RPC server. */
    result = xmlrpc_client_call(&env, SERVER_URL,
                                "sample.sumAndDifference", "(ii)",
                                (xmlrpc_int32) 5,
                                (xmlrpc_int32) 3);
    die_if_fault_occurred(&env);
    
    /* Parse our result value. */
    xmlrpc_parse_value(&env, result, "{s:i,s:i,*}",
                       "sum", &sum,
                       "difference", &difference);
    die_if_fault_occurred(&env);

    /* Print out our sum and difference. */
    printf("Sum: %d, Difference: %d\n", (int) sum, (int) difference);
    
    /* Dispose of our result value. */
    xmlrpc_DECREF(result);

    /* Shutdown our XML-RPC client library. */
    xmlrpc_env_clean(&env);
    xmlrpc_client_cleanup();

    return 0;
}

