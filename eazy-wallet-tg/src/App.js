import { useCallback, useEffect, useState } from 'react';
import './App.css';
import { QRCodeSVG } from 'qrcode.react'
import Button from './components/Button/Button'

const tg = window.Telegram.WebApp;

function copyToClipboard(wallet_adress) {
    const el = document.createElement('textarea');
    el.value = wallet_adress;
    el.setAttribute('readonly', '');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
}

function App() {
	useEffect(() => {
		tg.ready();
	}, [])

	const OnClose = useCallback(() => {
		tg.close();
	}, [])

	useEffect(() => {
		tg.onEvent('mainButtonClicked', OnClose)
		return () => {
			tg.offEvent('mainButtonClicked', OnClose)
		}
	}, [OnClose])

	useEffect(() => {
		tg.MainButton.hide();
		tg.MainButton.setParams({
			text: 'Закрыть'
		})
	}, [])

	const onCopyAddress = () => {
		copyToClipboard(wallet_adress);
		console.log(wallet_adress);
	}

	const [loading, setLoading] = useState(true);
	const loading_card = document.getElementById('loading');

	const queryParams = new URLSearchParams(window.location.search);
	const wallet_adress = queryParams.get("wallet_adress");
	const fgColor_text = tg.themeParams.text_color;

	if (loading_card) {
		setTimeout(() => {
			loading_card.style.display = "none";
			setLoading(false);
		}, 3000);

		tg.MainButton.show();

		return (
			!loading && (
			<div className='main'>
	
				<div className='block' id='top-text'>
					<h1>Scan For Send</h1>
				</div>
	
				<div className='block'>
					<QRCodeSVG className='qr-code-svg'
						size={256}
						includeMargin={false}
						imageSettings={{
							src: "money-cash.gif",
							x: undefined,
							y: undefined,
							width: 55,
							height: 55,
							excavate: true,
						}}
						bgColor="transparent"
						fgColor={fgColor_text}
						value={wallet_adress}
					/>
				</div>

				<div className='block'>
					<Button onClick={onCopyAddress}>Копировать адрес</Button>
				</div>
				
			</div>
		));
	}
}

export default App;