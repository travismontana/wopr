/*
 * Core config file
 * OS Env variables needed:
 * WOPR_ENVIRONMENT
 * WOPR_API_URL
 * 
 * 1. Get the environment variable
 * 2. use those to grab the main config
 *   ${WOPR_API_URL}/api/v2/config/all
 *   That retuns a json
 * 3. exports woprconfig 
 */

export interface WoprConfig {}