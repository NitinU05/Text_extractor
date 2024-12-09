const { ocr } = require("llama-ocr");

async function runOCR(filepath,apikey) {
    try{
        const markdown = await ocr({filePath,apiKey});
        console.log(markdown);
    }catch (error){
        console.error("Error:",error);
    }
}


runocr(process.argv[2], process.argv[3]);