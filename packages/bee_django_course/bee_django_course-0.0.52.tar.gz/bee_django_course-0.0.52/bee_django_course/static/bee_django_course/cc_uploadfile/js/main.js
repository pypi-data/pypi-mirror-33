/*
 * jQuery File Upload Plugin JS Example
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2010, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 */

/* global $, window */

$(function () {
    'use strict';
    $('#fileupload').fileupload({
        // 设置超时处理时间 超时时间3分钟 超时会重试
        timeout: 180000,
        maxChunkSize: 2097152, // 2MB
        dataType: 'json',
        limitConcurrentUploads: 1,
        // 文件重试
        maxRetries: 200,
        retryTimeout: 500
    });
});


