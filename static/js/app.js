console.log("FinGenie AI Loaded");

let currentConversationId = null;

const chatBox = document.getElementById("chat-box");
const input = document.getElementById("message");
const sendBtn = document.getElementById("send-btn");
const conversationList = document.getElementById("conversation-list");


/* ==========================
   SCROLL
========================== */

function scrollBottom() {

    chatBox.scrollTop = chatBox.scrollHeight;

}


/* ==========================
   WELCOME SCREEN
========================== */

function hideWelcome() {

    const welcome = document.querySelector(".welcome");

    if (welcome) {
        welcome.remove();
    }

}


function showWelcome() {

    chatBox.innerHTML = `
        <div class="welcome">

            <h2>👋 Welcome to FinGenie AI</h2>

            <p>
                Ask anything about Credit Cards,
                Personal Loans,
                Home Loans,
                EMI,
                Vehicle Loans,
                or CIBIL Score.
            </p>

        </div>
    `;

}


/* ==========================
   USER MESSAGE
========================== */

function addUserMessage(text) {

    const div = document.createElement("div");

    div.className = "user-message";

    div.textContent = text;

    chatBox.appendChild(div);

    scrollBottom();

}


/* ==========================
   BOT MESSAGE
========================== */

function addBotMessage(text) {

    const div = document.createElement("div");

    div.className = "bot-message";


    // Copy button

    const copyBtn = document.createElement("button");

    copyBtn.className = "copy-btn";

    copyBtn.innerHTML = '<i class="bi bi-copy"></i>';

    copyBtn.title = "Copy response";


    copyBtn.onclick = async function () {

        try {

            await navigator.clipboard.writeText(text);

            copyBtn.innerHTML =
                '<i class="bi bi-check-lg"></i>';

            copyBtn.title = "Copied";

            setTimeout(() => {

                copyBtn.innerHTML =
                    '<i class="bi bi-copy"></i>';

                copyBtn.title = "Copy response";

            }, 1500);

        } catch (error) {

            console.error("Copy failed:", error);

        }

    };


    // Message content

    const content = document.createElement("div");

    content.className = "bot-content";

    content.innerHTML = marked.parse(text || "");


    div.appendChild(copyBtn);

    div.appendChild(content);

    chatBox.appendChild(div);

    scrollBottom();

}


/* ==========================
   THINKING
========================== */

function showThinking() {

    hideThinking();

    const div = document.createElement("div");

    div.className = "bot-message";

    div.id = "thinking";

    div.innerHTML = `
        <div class="typing">

            <span></span>
            <span></span>
            <span></span>

        </div>
    `;

    chatBox.appendChild(div);

    scrollBottom();

}


function hideThinking() {

    const thinking =
        document.getElementById("thinking");

    if (thinking) {
        thinking.remove();
    }

}


/* ==========================
   SEND MESSAGE
========================== */

async function sendMessage() {

    const message = input.value.trim();

    if (message === "") {
        return;
    }


    hideWelcome();

    addUserMessage(message);

    input.value = "";

    sendBtn.disabled = true;


    sendBtn.innerHTML = `
        <div class="spinner"></div>
    `;


    showThinking();


    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                message: message,

                conversation_id:
                    currentConversationId

            })

        });


        if (!response.ok) {

            const errorText =
                await response.text();

            throw new Error(
                `Server Error ${response.status}: ${errorText}`
            );

        }


        const data =
            await response.json();


        console.log("Chat response:", data);


        hideThinking();


        /*
         * Backend should return:
         *
         * {
         *   reply: "...",
         *   conversation_id: 123
         * }
         */

        if (data.conversation_id) {

            currentConversationId =
                data.conversation_id;

        }


        if (data.reply) {

            addBotMessage(data.reply);

        } else {

            addBotMessage(
                "❌ No response received from AI."
            );

        }


        await loadConversations();


    } catch (error) {

        console.error(
            "Chat error:",
            error
        );


        hideThinking();


        addBotMessage(
            "❌ " + error.message
        );


    } finally {

        sendBtn.disabled = false;


        sendBtn.innerHTML = `
            <i class="bi bi-send-fill"></i>
        `;


        input.focus();

    }

}


/* ==========================
   LOAD CONVERSATIONS
========================== */

async function loadConversations() {

    try {

        const response =
            await fetch("/conversations");


        if (!response.ok) {

            throw new Error(
                `Failed to load conversations: ${response.status}`
            );

        }


        const conversations =
            await response.json();


        conversationList.innerHTML = "";


        conversations.forEach(
            conversation => {

                const item =
                    document.createElement("div");


                item.className =
                    "conversation-item";


                if (
                    conversation.id ===
                    currentConversationId
                ) {

                    item.classList.add("active");

                }


                item.innerHTML = `

                    <div class="conversation-row">

                        <span class="conversation-title">

                            <i class="bi bi-chat-left-text"></i>

                            ${escapeHtml(
                                conversation.title
                            )}

                        </span>


                        <button
                            class="delete-btn"
                            title="Delete conversation"
                        >

                            <i class="bi bi-trash"></i>

                        </button>

                    </div>

                `;


                /* ==========================
                   OPEN CONVERSATION
                ========================== */

                item.onclick = function () {

                    currentConversationId =
                        conversation.id;

                    loadMessages(
                        conversation.id
                    );

                    loadConversations();

                };


                /* ==========================
                   DELETE
                ========================== */

                const deleteBtn =
                    item.querySelector(
                        ".delete-btn"
                    );


                deleteBtn.onclick =
                    async function (event) {

                        event.stopPropagation();


                        const confirmed =
                            confirm(
                                "Delete this conversation?"
                            );


                        if (!confirmed) {
                            return;
                        }


                        try {

                            const response =
                                await fetch(
                                    `/conversation/${conversation.id}`,
                                    {
                                        method: "DELETE"
                                    }
                                );


                            if (!response.ok) {

                                throw new Error(
                                    "Failed to delete conversation"
                                );

                            }


                            if (
                                currentConversationId ===
                                conversation.id
                            ) {

                                currentConversationId =
                                    null;

                                showWelcome();

                            }


                            await loadConversations();


                        } catch (error) {

                            console.error(
                                "Delete error:",
                                error
                            );

                            alert(
                                "Failed to delete conversation."
                            );

                        }

                    };


                conversationList.appendChild(item);

            }
        );


    } catch (error) {

        console.error(
            "Conversation loading error:",
            error
        );

    }

}


/* ==========================
   LOAD MESSAGES
========================== */

async function loadMessages(
    conversationId
) {

    try {

        const response =
            await fetch(
                `/messages/${conversationId}`
            );


        if (!response.ok) {

            throw new Error(
                "Failed to load messages"
            );

        }


        const messages =
            await response.json();


        currentConversationId =
            conversationId;


        chatBox.innerHTML = "";


        if (messages.length === 0) {

            showWelcome();

            return;

        }


        messages.forEach(msg => {

            if (msg.role === "user") {

                addUserMessage(
                    msg.message
                );

            } else {

                addBotMessage(
                    msg.message
                );

            }

        });


        scrollBottom();


    } catch (error) {

        console.error(
            "Message loading error:",
            error
        );

    }

}


/* ==========================
   NEW CHAT
========================== */

const newChatBtn =
    document.getElementById("new-chat");


if (newChatBtn) {

    newChatBtn.onclick =
        function () {

            currentConversationId =
                null;


            showWelcome();


            loadConversations();


            input.focus();

        };

}


/* ==========================
   ENTER KEY
========================== */

input.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage();

        }

    }
);


/* ==========================
   HTML ESCAPE
========================== */

function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text || "";

    return div.innerHTML;

}


/* ==========================
   INITIAL LOAD
========================== */

loadConversations();

input.focus();