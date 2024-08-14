/* HTTP GET/POST 방식 axios 기반 통신 axios 는 Promise API를 지원함 */



// #################################################
// ########## 카드 클릭 후 API 요청 후 디테일 페이지 표시
function convertLineBreaks(text) {
    return text.replace(/\n\n/g, '<br>');// 줄바꿈 정제
}

function getContent(category, title, id) {
    axios(`https://baduks.store/util/content?category=${category}&id=${id}`, {
        method: "get",
    }).then((response) => {
        const contentPage = document.querySelector("section.content-page");
        // category, title
        contentPage.querySelector("div.roadmap-title").textContent = response.data['category'];
        document.querySelector("div.article-title").textContent = title;
        // author, date, img_link
        contentPage.querySelector("div.article-author").textContent = response.data['author'];
        contentPage.querySelector("div.article-date").textContent = response.data['date'];
        contentPage.querySelector('img').src = response.data['img_link'];
        // audio 표시
        document.body.querySelector('audio').querySelector('source').src = `util/audio/${id}.mp3`
        document.body.querySelector('audio').load();
        // description
        const descriptionText = response.data['description'];
        // 줄바꿈 인식될 수 있도록 <br> 변환 후 innerHTML
        contentPage.querySelector("div.description").innerHTML = convertLineBreaks(descriptionText);
        // summary
        if (response.data['summary'] === undefined) { contentPage.querySelector("div.summary").innerHTML = "Summary data is not available yet.😢"; }
        else { contentPage.querySelector("div.summary").innerHTML = response.data['summary']; }
        // source link
        contentPage.querySelector("a.article-sourcelink").textContent = response.data['destination_link'];
        contentPage.querySelector("a.article-sourcelink").href = response.data['destination_link'];
    }).catch((error) => {
        console.log(error);
        var img = document.querySelector('section.content-page').querySelector('img');
        img.src = 'img/no_img.webp' // 이미지 데이터 없으면 no_img 표시
    })
}
// ########################################

// ######################################
// ########## 백엔드에서 데이터 가져와서 화면에 표시하기
// cardData = {'AI':[{},{},...], 'APPS':[{},{},...] }
function displayNewsCards(cardData) {
    const categoryKeys = Object.keys(cardData).sort();
    let section = document.querySelector('section.card-page')
    for (let i = 0; i < categoryKeys.length; i++) {
        const title = `${categoryKeys[i]}`
        let cardInnerHtmlHead =
            `
        <section>
            <div class="inner">
                <div class="roadmap-container">
                    <div class="roadmap-title-container">
                        <div class="roadmap-title">${title}</div>
                        <div class="arrow-container">
                            <i class="fas fa-chevron-circle-left slide-prev"></i>
                            <i class="fas fa-chevron-circle-right slide-next"></i>
                        </div>
                    </div>
                    <ul class="class-list" data-position="0">
            `
        let cardList = cardData[categoryKeys[i]]
        cardList.sort((a, b) => {
            // 날짜 객체로 변환
            const dateA = new Date(a.date);
            const dateB = new Date(b.date);

            // 최신 날짜가 먼저 오도록 내림차순 정렬
            return dateB - dateA;
        });

        for (let j = 0; j < cardList.length; j++) {
            if (cardList[j]['img_link'] === null) {
                img_link = "img/no_img.webp";
            } else { img_link = cardList[j]['img_link'] };
            cardInnerHtmlHead +=
                `
                <li class="class-card">
                <img src=${img_link} alt="news-img" class="class-image" />
                    <div class="class-container">
                    <div class="class-skill">
                        <div class="class-type">${cardList[j]['date']}</div>
                    </div>
                    <div class="class-desc">
                        <div class="class-detail" data-cardinfoid="${cardList[j]['id']}">${cardList[j]['title']}</div>
                    </div>
                    </div>
                </li>
                `
        }
        let cardInnerHtmlTail = `
                    </ul>
                </div>
            </div>
        </section>
        `;
        cardInnerHtml = cardInnerHtmlHead + cardInnerHtmlTail
        section.insertAdjacentHTML('beforeend', cardInnerHtml);
    }
}

function getNewsCards() {
    return new Promise((resolve) => {
        axios("https://baduks.store/util/newscards", {
            method: "get",
        }).then((response) => {
            resolve(response.data);
        }).catch((error) => {
            console.log(error);
        })
    })
}
// #################################

// #########################################
// ################### 카드메뉴 좌우 이동 시키는 기능
function transformNext(event) {
    const slideNext = event.target;
    const slidePrev = slideNext.previousElementSibling;
    const classList = slideNext.parentElement.parentElement.nextElementSibling;
    let activeLi = classList.getAttribute('data-position');
    // 하나의 카드라도 왼쪽으로 이동했다면, 오른쪽으로 갈 수 있음
    if (Number(activeLi) < 0) {
        activeLi = Number(activeLi) + 260;
        // 왼쪽에 있던 카드가 오른쪽으로 갔다면, 다시 왼쪽으로 갈 수 있으므로 PREV 버튼 활성화
        slidePrev.style.color = '#2f5958'; // 활성화
        slidePrev.classList.add('slide-prev-hover'); // 하버 반응 활성화
        slidePrev.addEventListener('click', transformPrev);
        if (Number(activeLi) === 0) {
            slideNext.style.color = '#cfd8dc'; // 비활성화
            slideNext.classList.remove('slide-next-hover');
            slideNext.removeEventListener('click', transformNext);
        }
    }
    classList.style.transition = 'transform 0.2s ease'; // 1초동안 자연스러운 이동
    classList.style.transform = 'translateX(' + String(activeLi) + 'px)'; // x축 기준으로 이동
    classList.setAttribute('data-position', activeLi);
}

// event = 어떤 event가 실행된건지, 해당 이벤트가 발생한 요소는 무엇인지에 대한 정보를 담고있음
function transformPrev(event) {
    // slidePrev는 클릭 이벤트가 발생한 요소
    const slidePrev = event.target;
    const slideNext = slidePrev.nextElementSibling;
    // ul 태그 선택
    // classList = 카드뭉치
    const classList = slidePrev.parentElement.parentElement.nextElementSibling;
    // activeLi의 초기값은 0
    let activeLi = classList.getAttribute('data-position');
    // liList = 카드 낱개 리스트
    const liList = classList.getElementsByTagName('li');
    // 왼쪽으로 이동할 수 있는지 체크
    // 카드뭉치의 길이 < 카드 개수 * 260 + 0
    // classList.clientWidth는 화면 크기에 따라 달라질 수 있음
    // liList.length*260은 카드를 쭉 폈을 때 길이
    if (classList.clientWidth < (liList.length * 260 + Number(activeLi))) {
        activeLi = Number(activeLi) - 260;
        // 오른쪽 끝까지 다 갔는지 체크 -> 다 갔으면 if문 안으로
        if (classList.clientWidth > (liList.length * 260 + Number(activeLi))) {
            slidePrev.style.color = '#cfd8dc'; // prev버튼 회색(비활성화)
            slidePrev.classList.remove('slide-prev-hover'); // prev 하버 반응 제거
            slidePrev.removeEventListener('click', transformPrev); // 더 이상 해당 이벤트가 발생했을 때 그 코드가 실행되지 않도록
        }
        slideNext.style.color = '#2f5958'; // next버튼 활성화
        slideNext.classList.add('slide-next-hover');
        slideNext.addEventListener('click', transformNext);
    }
    classList.style.transition = 'transform 0.2s ease'; // 1초동안 자연스러운 이동
    classList.style.transform = 'translateX(' + String(activeLi) + 'px)'; // x축 기준으로 이동
    classList.setAttribute('data-position', activeLi);
}

function leftRightArrow() {
    // 처음에 페이지 나타낼 때, 카드개수가 적으면 화살표 표시안하고, 카드개수가 많으면 화살표 표시하기
    // slidePrevList = 왼쪽 화살표(prev)가 담긴 리스트
    const slidePrevList = document.getElementsByClassName('slide-prev');
    for (let i = slidePrevList.length - 1; i >= 0; i--) {
        // ul 태그 선택 -> classList = 카드 뭉치
        let classList = slidePrevList[i].parentElement.parentElement.nextElementSibling;
        // liList = 카드 뭉치 속 카드의 낱개가 담긴 리스트
        let liList = classList.getElementsByTagName('li');
        // 카드가 ul 태그 너비보다 넓으면, 왼쪽 이동 버튼 활성화,
        // 오른쪽 버튼은 현재 맨 첫 카드 위치이므로 비활성화
        // 카드 240픽셀에, 마진 10+10 => 260픽셀
        if (classList.clientWidth < (liList.length * 260)) {
            slidePrevList[i].classList.add('slide-prev-hover'); // 하버했을 때 반응하기
            slidePrevList[i].addEventListener('click', transformPrev); //클릭 이벤트 발생
        } else {
            // 태그 삭제시, 부모 요소에서 removeChild를 통해 삭제해야 함
            // 1.먼저 부모 요소를 찾아서, 2.부모 요소의 자식 요소로 있는 Prev와 Next 요소를 삭제하기
            const arrowContainer = slidePrevList[i].parentElement;
            // next 먼저 지우고
            arrowContainer.removeChild(slidePrevList[i].nextElementSibling);
            // 그다음 prev 지우기
            arrowContainer.removeChild(slidePrevList[i]);
        }

    }
}
// #############################################################

// ###########################################################
// ################카드 드래그 해서 옮기기 기능

let currentActiveLi;
let nowActiveLi;
let mouseStart;

function processTouchMove(event) {
    event.preventDefault();// 원래 사진 잡아서 끌면 딸려가는것이 디폴트인데, 그것을 없앰
    // 이벤트 객체 event에서 마우스 또는 터치 위치를 가져오는 방식
    let currentX = event.clientX || event.touches[0].screenX;
    nowActiveLi = Number(currentActiveLi) + (Number(currentX) - Number(touchstartX));
    currentClassList.style.transition = 'transform 0s linear'; // 0초만에 바로 옮기기
    currentClassList.style.transform = 'translateX(' + String(nowActiveLi) + 'px)';
}

function processTouchStart(event) {
    mouseStart = true;
    event.preventDefault(); // 원래 사진 잡아서 끌면 딸려가는것이 디폴트인데, 그것을 없앰
    touchstartX = event.clientX || event.touches[0].screenX; // 마우스 위치 또는 스마트폰 터치의 위치 값을 가져오기
    currentImg = event.target; // 해당 img 태그
    // mousemove는 마우스 커서가 움직이는 동안 계속 발생하는 이벤트
    currentImg.addEventListener('mousemove', processTouchMove);
    currentImg.addEventListener('mouseup', processTouchEnd);
    currentImg.addEventListener('touchmove', processTouchMove);
    currentImg.addEventListener('touchend', processTouchEnd);
    currentClassList = currentImg.parentElement.parentElement;
    currentActiveLi = currentClassList.getAttribute('data-position');

}

function processTouchEnd(event) {
    event.preventDefault(); // 원래 사진 잡아서 끌면 딸려가는것이 디폴트인데, 그것을 없앰

    if (mouseStart == true) {
        currentImg.removeEventListener('mousemove', processTouchMove);
        currentImg.removeEventListener('mouseup', processTouchMove);

        currentImg.removeEventListener('touchmove', processTouchMove);
        currentImg.removeEventListener('touchend', processTouchMove);

        // 카드가 다시 맨 앞으로 배치되도록 초기 상태로 이동
        currentClassList.style.transition = 'transform 1s ease';
        currentClassList.style.transform = 'translateX(0px)';
        currentClassList.setAttribute('data-position', 0);

        //
        let eachSlidePrev = currentClassList.previousElementSibling.children[1].children[0];
        let eachSlideNext = currentClassList.previousElementSibling.children[1].children[1];
        let eachLiList = currentClassList.getElementsByTagName('li');
        if (currentClassList.clientWidth < (eachLiList.length * 260)) {
            // 왼쪽 화살표 활성화 시키기
            eachSlidePrev.style.color = '#2f5958';
            eachSlidePrev.classList.add('slide-prev-hover');
            eachSlidePrev.addEventListener('click', transformPrev);

            // 오른쪽 화살표 비활성화 시키기
            eachSlideNext.style.color = '#cfd8dc';
            eachSlideNext.classList.remove('slide-next-hover');
            eachSlideNext.addEventListener('click', transformPrev);
        }
    }
    mouseStart = false;
}

// window 객체는 브라우저 환경에서 전역 객체(global object)
// dragend 이벤트: 사용자가 요소를 드래그한 후 마우스 버튼을 놓을 때 발생합니다. 이 이벤트는 드래그 작업이 끝날 때 트리거됩니다.
// mouseup 이벤트: 사용자가 마우스 버튼을 눌렀다가 놓을 때 발생합니다.
window.addEventListener('dragend', processTouchEnd);
window.addEventListener('mouseup', processTouchEnd);

function cardDragMove() {
    const classImgLists = document.querySelectorAll('ul li img');
    for (let i = 0; i < classImgLists.length; i++) {
        // mousedown 이벤트는 사용자가 마우스 버튼을 눌렀을 때 발생하는 이벤트
        classImgLists[i].addEventListener('mousedown', processTouchStart);
        classImgLists[i].addEventListener('touchstart', processTouchStart);
    }
}
// #####################################################

// #######################################
// ########## 게시물 클릭했을 떄, 게시물 웹페이지 들어가기

let state = {};
function clickCard(event) {
    if (window.scrollY > 0)
        window.scrollTo({ top: 0, behavior: "auto" }); // 스크롤 맨 위로 올리기
    let getLi = event.target
    while (getLi.tagName != "LI") {
        getLi = getLi.parentElement;
    }
    const cardPage = document.body.querySelector('section.card-page');
    const contentPage = document.body.querySelector('section.content-page');
    window.history.pushState(state, '', window.location.pathname);
    cardPage.style.display = "none";
    contentPage.style.display = "block";
    title = getLi.querySelector('div.class-detail');
    cardInfoId = title.getAttribute('data-cardinfoid')
    category = getLi.parentElement.parentElement.querySelector('.roadmap-title')
    getContent(category.textContent, title.textContent, cardInfoId);
}

function readyToClick() {
    const cardByCategory = document.getElementsByClassName('class-list');
    for (let i = 0; i < cardByCategory.length; i++) {
        cardTitleList = cardByCategory[i].getElementsByClassName('class-card');
        for (let j = 0; j < cardTitleList.length; j++) {
            cardTitleList[j].addEventListener('click',
                (event) => { clickCard(event) }); //클릭 이벤트 발생
        }
    }
}
// #########################################

// #########################################
// ####################백엔드 API 요청 후 실행할 함수들 (동기적 처리)
getNewsCards().then((cardData) => {
    displayNewsCards(cardData);
}).then(() => {
    leftRightArrow();
    cardDragMove();
    readyToClick();
});
// ###############################################

// ###################################################
// ###################뒤로가기 및 앞으로 가기 발생 후 처리할 로직
window.addEventListener('popstate', function (event) {
    // 뒤로가기 또는 앞으로 가기 할 때 카드페이지가 이전과 반대로 설정
    // 디테일페이지도 마찬가지로 이전과 반대로 설정
    const cardSection = document.querySelector('.card-page');
    const contentPage = document.body.querySelector('section.content-page');
    if (cardSection.style.display === 'block') {
        cardSection.style.display = 'none'
    } else { cardSection.style.display = 'block' };
    if (contentPage.style.display === 'none') {
        contentPage.style.display = 'block'
    } else { contentPage.style.display = 'none' };
    // 뒤로가기 또는 앞으로가기 시 오디오 정지
    const audioElement = document.querySelector('audio');
    audioElement.pause();
    audioElement.currentTime = 0;
});
// ###########################################

// ##############################################
// ################## 위로 끝까지 올리는 버튼 기능
const backToTop = document.getElementById('backtotop');

const checkScroll = () => {
    let pageYOffset = window.scrollY;
    if (pageYOffset !== 0) {
        backToTop.classList.add('show')
    } else {
        backToTop.classList.remove('show')
    }
}

const moveBackToTop = () => {
    if (window.scrollY > 0)
        window.scrollTo({ top: 0, behavior: "smooth" })
}
// 스크롤 할 때마다 checkScroll 호출하기
window.addEventListener('scroll', checkScroll);
// 클릭했을 때 위로 쭉 올리기
backtotop.addEventListener('click', moveBackToTop);
// ###############################################
