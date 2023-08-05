
    var file_id = 0, drop_zone;



    if ((typeof File !== 'undefined') && !File.prototype.slice) {
      if(File.prototype.webkitSlice) {
        File.prototype.slice = File.prototype.webkitSlice;
      }

      if(File.prototype.mozSlice) {
        File.prototype.slice = File.prototype.mozSlice;
      }
    }

    if (!window.File || !window.FileReader || !window.FileList || !window.Blob || !File.prototype.slice) {
      //alert('File APIs are not fully supported in this browser. Please use latest Mozilla Firefox or Google Chrome.');
      alert('此浏览器不支持文件读取API. 请下载安装最新版本的Mozilla Firefox(火狐浏览器),Internet Explorer 10 (IE10)或者Google Chrome(谷歌浏览器).');

    }

    function hash_file(file, workers,index) {
    	
      var i, buffer_size, block, threads, reader, blob, handle_hash_block, handle_load_block;

      reader = new FileReader();

      handle_load_block = function (event) {

    	  if(uploadDatas[index].isCanceled){        		
        		return;
        }
        for( i = 0; i < workers.length; i += 1) {
          threads += 1;
          workers[i].postMessage({
            'message' : event.target.result,
            'block' : block
          });
        }
      };
      handle_hash_block = function (event) {

        threads -= 1;

        if(threads === 0) {
          if(block.end !== file.size) {
            block.start += buffer_size;
            block.end += buffer_size;

            if(block.end > file.size) {
              block.end = file.size;
              // 读完时，remove 监听
              removeHandle_hash_block_Listener();
            }
            
            reader.onload = handle_load_block;
            blob = file.slice(block.start, block.end);

            //reader.readAsBinaryString(blob);
            reader.readAsArrayBuffer(blob);
           
          }
        }
      };
      
      // 注销事件监听handle_hash_block，避免分块上传被打断
      function removeHandle_hash_block_Listener(){
      	for (i = 0; i < workers.length; i += 1) {
              workers[i].removeEventListener('message', handle_hash_block);
        }
      }
      
      buffer_size = 2 * 1024 * 1024;
      block = {
        'file_size' : file.size,
        'start' : 0
      };

      block.end = buffer_size > file.size ? file.size : buffer_size;
      threads = 0;

      for (i = 0; i < workers.length; i += 1) {
        workers[i].addEventListener('message', handle_hash_block);
      }
      
      reader.onload = handle_load_block;
      blob = file.slice(block.start, block.end);
      
      //reader.readAsBinaryString(blob);
      reader.readAsArrayBuffer(blob);
    }

    function handle_worker_event(index) {

      return function (event) {

        if (event.data.result) {
        	md5 = event.data.result;
        	uploadDatas[index].context.find('.rate').html('MD5计算：100%');
        	// md5 计算完毕后，进行断点续传
        	if(!uploadDatas[index].isCanceled){   
        		uploadDatas[index].md5=md5;
        		//uploadDatas[index].context.find("#start").attr('style',"");
            //md5校验完成后提交数据到服务器获取vid
            var myfiles=uploadDatas[index].files;
            
            for(var i=0;i<myfiles.length;i++){
                var file=myfiles[i];
                //向父窗口提交数据  
                var message={"index":index,"name":file.name,"size":file.size};
                window.parent.postMessage(message, "*");

            }

        	}
           //console.info("final MD5 = "+event.data.result);
        } else {
             uploadDatas[index].context.find('.rate').html('MD5计算：' + Math.round(event.data.block.end * 100 / event.data.block.file_size) + '%');
             //console.info("calculated MD5 = " + Math.round(event.data.block.end * 100 / event.data.block.file_size) + '%');
        }
      };
    }
    
    function handle_file_select(uploadData,index) {
      //处理显示数据
      uploadData.context.find('.rate').html('MD5计算中');   

      //console.log("开始计算md5 index="+index); 	

      var i, output, files, file, worker;
      files = uploadData.files;


      for (i = 0; i < files.length; i += 1) {
        file = files[i];
        workers = [];
        worker = new Worker('/js/fileupload/sparkmd5_worker.js');
        worker.addEventListener('message', handle_worker_event(index));
        workers.push(worker);

        //console.log("md5 worker..start....");

        hash_file(file, workers,index);
        

      }
    }


