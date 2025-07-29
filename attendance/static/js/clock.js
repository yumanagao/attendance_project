function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return null;
}

const statusElement = document.getElementById("status");
const scannerElementId = "reader";

// ✅ 初期化
const html5QrcodeScanner = new Html5Qrcode(scannerElementId);

function onScanSuccess(decodedText, decodedResult) {
    statusElement.textContent = "スキャン成功！送信中...";

    // 一時停止（読み取りの連続防止）
    html5QrcodeScanner.pause();

    fetch("/attendance/clock_in_out/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ qr_data: decodedText })
    })
    .then(response => response.json())
    .then(data => {
        statusElement.textContent = data.message || "打刻完了";
    
        const resultMessage = document.getElementById("result-message");
    
        if (data.status === "success" && data.name && data.message_type) {
            if (data.message_type === "clock_in") {
                resultMessage.textContent = `${data.name}さん、おはようございます！`;
            } else if (data.message_type === "clock_out") {
                resultMessage.textContent = `${data.name}さん、お疲れ様でした！`;
            } else {
                resultMessage.textContent = "";
            }
        } else {
            resultMessage.textContent = "";
        }
    
        // ✅ 数秒後に再開
        setTimeout(() => {
            html5QrcodeScanner.resume();
            statusElement.textContent = "QRコードをスキャンしてください";
            resultMessage.textContent = "";
        }, 4000);
    })
    .catch(error => {
        console.error("送信エラー:", error);
        statusElement.textContent = "送信に失敗しました。再試行します...";

        // ✅ エラー時も再開
        setTimeout(() => {
            html5QrcodeScanner.resume();
            statusElement.textContent = "QRコードをスキャンしてください";
        }, 2000);
    });
}

function onScanFailure(error) {
    // エラー無視（必要に応じて console 出力可能）
}

// ✅ カメラ起動
Html5Qrcode.getCameras().then(cameras => {
    if (cameras && cameras.length) {
        const cameraId = cameras[0].id;
        html5QrcodeScanner.start(
            cameraId,
            { fps: 10, qrbox: 250 },
            onScanSuccess,
            onScanFailure
        );
    } else {
        statusElement.textContent = "カメラが見つかりません。";
    }
}).catch(err => {
    statusElement.textContent = "カメラの起動に失敗しました。";
    console.error("カメラエラー:", err);
});