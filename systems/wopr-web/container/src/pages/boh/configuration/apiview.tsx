import React, { useEffect, useState } from 'react';
import JsonView from 'react18-json-view';
import 'react18-json-view/src/style.css';
import { apiUrl } from '@lib/api';

/*
 * This will grab the json from ${apiUrl}/api/v1/config/all?environment=${env}
 * the page will ask 