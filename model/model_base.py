from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from abc import abstractmethod

from system.message import Info
from system.message import BaseMessageDataType
from model.strategy_type import StrategyType
from model.base import BaseStrategy

import base64
from io import BytesIO
import requests

from openai import OpenAI
from google import genai
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import TextContentItem, ImageContentItem, ImageUrl, SystemMessage, UserMessage, AssistantMessage

from transformers import AutoModelForCausalLM, AutoTokenizer, Qwen2_5_VLForConditionalGeneration, AutoProcessor, GenerationConfig, Gemma3ForConditionalGeneration
from qwen_vl_utils import process_vision_info
import transformers
import torch


class ModelBase(BaseStrategy):
    strategy_type: StrategyType = StrategyType.NoneType
    name: str = ''
    max_new_tokens: int = 2048

    images: List[Any] = []
    history: List[Any] = []
    completion_tokens: List[int] = []
    reasoning: List[Any] = []
    reasoning_tokens: List[int] = []
    total_tokens: List[int] = []
    total_usage: int = 0

    model: Any = None
    tokenizer: Any = None
    processor: Any = None

    def load_model(self):
        if self.name.lower() in ['gpt-4.1', 'o4-mini', 'grok-3-mini-beta', 'gemini-2.5-pro-preview-03-25', 'deepseek-reasoner', 'deepseek-chat', 'phi-4-multimodal-instruct']:
            pass

        if 'llama' in self.name.lower():
            self.model = transformers.pipeline(
                "text-generation",
                model="meta-llama/Llama-3.3-70B-Instruct",
                model_kwargs={"torch_dtype": torch.bfloat16},
                trust_remote_code=True,
                device_map="auto",
            )
            self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.3-70B-Instruct")
        
        if 'gemma' in self.name.lower():
            self.model = Gemma3ForConditionalGeneration.from_pretrained(
                "google/gemma-3-27b-it",
                device_map="auto",
            ).eval()
            self.processor = AutoProcessor.from_pretrained("google/gemma-3-27b-it")
            self.tokenizer = AutoTokenizer.from_pretrained("google/gemma-3-27b-it")

        if 'qwq' in self.name.lower():
            self.model = AutoModelForCausalLM.from_pretrained(
                "Qwen/QwQ-32B",
                torch_dtype="auto",
                device_map="auto"
            )
            self.tokenizer = AutoTokenizer.from_pretrained("Qwen/QwQ-32B")
        
        if 'qwen' in self.name.lower():
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                "Qwen/Qwen2.5-VL-72B-Instruct",
                trust_remote_code=True,
                attn_implementation="flash_attention_2",
                device_map="auto",
            )
            self.tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-VL-72B-Instruct")
            self.processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-72B-Instruct")


    def process_multimodal_message(self, message_data: Any, with_history: bool):
        if self.name.lower() in ['gpt-4.1', 'o4-mini']:
            tmp = []
            for item in message_data:
                if item.type == 'text':
                    tmp.append({"type": "text", "text": item.data})
                else:
                    buffered = BytesIO()
                    item.data.save(buffered, format="JPEG") 
                    tmp.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"}})
            if len(self.history) == 0 or with_history is False:
                data = [{"role": "user", "content": tmp}]
                message_list = data
            else:
                data = [{"role": "user", "content": tmp}]
                message_list = self.history.copy()
                message_list.extend(data)
            return data, message_list
        elif self.name.lower() in ['gemini-2.5-pro-preview-03-25']:
            message_list = []
            for item in message_data:
                message_list.append(item.data)
            return None, message_list
        elif 'gemma' in self.name.lower():
            tmp = []
            for item in message_data:
                if item.type == 'text':
                    tmp.append({"type": "text", "text": item.data})
                else:
                    buffered = BytesIO()
                    item.data.save(buffered, format="JPEG") 
                    tmp.append({"type": "image", "image": f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"})
            if len(self.history) == 0 or with_history is False:
                data = [{"role": "user", "content": tmp}]
                message_list = data
            else:
                data = [{"role": "user", "content": tmp}]
                message_list = self.history.copy()
                message_list.extend(data)
            return data, message_list
        elif 'qwen' in self.name.lower():
            tmp = []
            for item in message_data:
                if item.type == 'text':
                    tmp.append({"type": "text", "text": item.data})
                else:
                    buffered = BytesIO()
                    item.data.save(buffered, format="JPEG") 
                    tmp.append({"type": "image", "image": f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"})
            if len(self.history) == 0 or with_history is False:
                data = [{"role": "user", "content": tmp}]
                message_list = data
            else:
                data = [{"role": "user", "content": tmp}]
                message_list = self.history.copy()
                message_list.extend(data)
            return data, message_list
        elif 'phi' in self.name.lower():
            tmp = []
            for item in message_data:
                if item.type == 'text':
                    tmp.append(TextContentItem(text=item.data))
                else:
                    buffered = BytesIO()
                    item.data.save(buffered, format="JPEG") 
                    tmp.append(ImageContentItem(image_url=ImageUrl(url=f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}")))
            if len(self.history) == 0 or with_history is False:
                data = [SystemMessage(content=tmp)]
                message_list = data
            else:
                data = [UserMessage(content=tmp)]
                message_list = self.history.copy()
                message_list.extend(data)
            return data, message_list


    def process_text_message(self, message_data: Any, with_history: bool):
        if self.name.lower() in ['gpt-4.1', 'o4-mini', 'grok-3-mini-beta']:
            if len(self.history) == 0 or with_history is False:
                data = [{"role": "system", "content": message_data}]
                message_list = data
            else:
                data = [{"role": "user", "content": message_data}]
                message_list = self.history.copy()
                message_list.extend(data)
            return data, message_list
        elif self.name.lower() in ['gemini-2.5-pro-preview-03-25']:
            message_list = [message_data]
            return None, message_list
        elif self.name.lower() in ['deepseek-reasoner', 'deepseek-chat'] or 'qwq' in self.name.lower():
            if len(self.history) == 0 or with_history is False:
                data = [{"role": "user", "content": message_data}]
                message_list = data
            else:
                data = [{"role": "user", "content": message_data}]
                message_list = self.history.copy()
                message_list.extend(data)
            return data, message_list
        elif 'gemma' in self.name.lower():
            if len(self.history) == 0 or with_history is False:
                data = [{"role": "user", "content": [{"type": "text", "text": message_data}]}]
                message_list = data
            else:
                data = [{"role": "user", "content": [{"type": "text", "text": message_data}]}]
                message_list = self.history.copy()
                message_list.extend(data)
            return data, message_list
        elif 'llama' in self.name.lower():
            if len(self.history) == 0 or with_history is False:
                data = [{"role": "system", "content": message_data}]
                message_list = data
            else:
                data = [{"role": "user", "content": message_data}]
                message_list = self.history.copy()
                message_list.extend(data)
            return data, message_list
        elif 'qwen' in self.name.lower():
            if len(self.history) == 0 or with_history is False:
                data = [{"role": "user", "content": [{"type": "text", "text": message_data}]}]
                message_list = data
            else:
                data = [{"role": "user", "content": [{"type": "text", "text": message_data}]}]
                message_list = self.history.copy()
                message_list.extend(data)
            return data, message_list
        elif 'phi' in self.name.lower():
            if len(self.history) == 0 or with_history is False:
                data = [SystemMessage(content=[TextContentItem(text=message_data)])]
                message_list = data
            else:
                data = [UserMessage(content=[TextContentItem(text=message_data)])]
                message_list = self.history.copy()
                message_list.extend(data)
            return data, message_list

    def get_model_stats(self, response: Any, input_token_count: int):
        # reasoning content
        reasoning_content = None
        if self.name.lower() in ['grok-3-mini-beta', 'deepseek-reasoner']:
            reasoning_content = response.choices[0].message.reasoning_content
        elif 'qwq' in self.name.lower():
            reasoning_content = self.tokenizer.batch_decode(response, skip_special_tokens=True)[0]
            reasoning_content = reasoning_content.split('</think>')[0]
 
        # reasoning token count
        reasoning_token_count = 0
        if self.name.lower() in ['o4-mini', 'grok-3-mini-beta', 'deepseek-reasoner']:
            reasoning_token_count = response.usage.completion_tokens_details.reasoning_tokens
        elif self.name.lower() == 'gemini-2.5-pro-preview-03-25':
            reasoning_token_count = response.usage_metadata.thoughts_token_count
        elif 'qwq' in self.name.lower():
            reasoning_token_count = response[0].tolist().index(151668) + 1

        # completion token count
        completion_token_cinput_tokensount = 0
        if self.name.lower() in ['gpt-4.1', 'grok-3-mini-beta', 'deepseek-chat']:
            completion_token_count = response.usage.completion_tokens
        elif self.name.lower() in ['o4-mini', 'deepseek-reasoner']:
            completion_token_count = response.usage.completion_tokens - reasoning_token_count
        elif self.name.lower() == 'gemini-2.5-pro-preview-03-25':
            completion_token_count = response.usage_metadata.candidates_token_count
        elif 'qwq' in self.name.lower():
            completion_token_count = response[0].shape[0] - reasoning_token_count
        elif 'gemma' in self.name.lower():
            completion_token_count = self.tokenizer(response, return_tensors="pt").input_ids.shape[1]
        elif 'llama' in self.name.lower():
            completion_token_count = self.tokenizer(response[0]["generated_text"][-1]["content"], return_tensors="pt").input_ids.shape[1]
        elif 'qwen' in self.name.lower():
            completion_token_count = self.tokenizer(response, return_tensors="pt").input_ids.shape[1]
        elif 'phi' in self.name.lower():
            completion_token_count = response.usage.completion_tokens

        # total token count
        total_token_count = 0
        if self.name.lower() in ['gpt-4.1', 'o4-mini', 'grok-3-mini-beta', 'deepseek-reasoner', 'deepseek-chat']:
            total_token_count = response.usage.total_tokens
        elif self.name.lower() == 'gemini-2.5-pro-preview-03-25':
            total_token_count = response.usage_metadata.total_token_count
        elif 'phi' in self.name.lower():
            total_token_count = response.usage.total_tokens
        elif 'qwq' in self.name.lower():
            total_token_count = input_token_count + completion_token_count + reasoning_token_count
        else:
            total_token_count = input_token_count + completion_token_count

        self.total_usage += total_token_count
        return reasoning_content, completion_token_count, reasoning_token_count, total_token_count

    def generate(self, message_data: Any, with_history: bool = True):
        ########TOKEN########
        openai_client = OpenAI(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        )
        grok_client = OpenAI(
            base_url="https://api.x.ai/v1",
            api_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        )
        gemini_client = genai.Client(api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        deepseek_client = OpenAI(
            base_url="https://api.deepseek.com",
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        )
        phi_client = ChatCompletionsClient(endpoint= "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", credential=AzureKeyCredential("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"))
        ####################

        if self.name.lower() == 'gpt-4.1' or self.name.lower() == 'o4-mini':
            if type(message_data) == list:
                data, message_list = self.process_multimodal_message(message_data, with_history)

                if self.name.lower() == 'gpt-4.1':
                    response = openai_client.chat.completions.create(
                        model=self.name,
                        messages=message_list,
                        max_completion_tokens=self.max_new_tokens,
                    )
                else:
                    response = openai_client.chat.completions.create(
                        model=self.name,
                        messages=message_list,
                    )

                reasoning_content, completion_token_count, reasoning_token_count, total_token_count = self.get_model_stats(response, None)

                return response.choices[0].message.content, data + [{"role": "assistant", "content": [{"type": "text", "text": response.choices[0].message.content}]}], reasoning_content, completion_token_count, reasoning_token_count, total_token_count
            else:
                data, message_list = self.process_text_message(message_data, with_history)

                if self.name.lower() == 'gpt-4.1':
                    response = openai_client.chat.completions.create(
                        model=self.name,
                        messages=message_list,
                        max_completion_tokens=self.max_new_tokens,
                    )
                else:
                    response = openai_client.chat.completions.create(
                        model=self.name,
                        messages=message_list,
                    )

                reasoning_content, completion_token_count, reasoning_token_count, total_token_count = self.get_model_stats(response, None)

                return response.choices[0].message.content, data + [{"role": "assistant", "content": response.choices[0].message.content}], reasoning_content, completion_token_count, reasoning_token_count, total_token_count

        elif 'grok' in self.name.lower():
            data, message_list = self.process_text_message(message_data, with_history)

            response = grok_client.chat.completions.create(
                model=self.name,
                reasoning_effort="high",
                messages=message_list,
            )

            reasoning_content, completion_token_count, reasoning_token_count, total_token_count = self.get_model_stats(response, None)

            return response.choices[0].message.content, data + [{"role": "assistant", "content": response.choices[0].message.content}], reasoning_content, completion_token_count, reasoning_token_count, total_token_count

        elif 'gemini' in self.name.lower():
            if with_history:
                model = gemini_client.chats.create(
                    model=self.name,
                    history=self.history
                )
            else:
                model = gemini_client.chats.create(
                    model=self.name,
                    history=[]
                )
            if type(message_data) == list:
                _, message_list = self.process_multimodal_message(message_data, with_history)
                response = model.send_message(message_list)

                reasoning_content, completion_token_count, reasoning_token_count, total_token_count = self.get_model_stats(response, None)

                return response.text, model.get_history()[-2:], reasoning_content, completion_token_count, reasoning_token_count, total_token_count
            else:
                _, message_list = self.process_text_message(message_data, with_history)
                response = model.send_message(message_list)

                reasoning_content, completion_token_count, reasoning_token_count, total_token_count = self.get_model_stats(response, None)

                return response.text, model.get_history()[-2:], reasoning_content, completion_token_count, reasoning_token_count, total_token_count

        elif 'deepseek' in self.name.lower():
            data, message_list = self.process_text_message(message_data, with_history)

            if self.name.lower() == 'deepseek-reasoner':
                response = deepseek_client.chat.completions.create(
                    model=self.name,
                    messages=message_list,
                )
            else:
                response = deepseek_client.chat.completions.create(
                    model=self.name,
                    messages=message_list,
                    max_tokens=self.max_new_tokens,
                )

            reasoning_content, completion_token_count, reasoning_token_count, total_token_count = self.get_model_stats(response, None)

            return response.choices[0].message.content, data + [{"role": "assistant", "content": response.choices[0].message.content}], reasoning_content, completion_token_count, reasoning_token_count, total_token_count

        elif 'gemma' in self.name.lower():
            if type(message_data) == list:
                data, message_list = self.process_multimodal_message(message_data, with_history)

                inputs = self.processor.apply_chat_template(
                    message_list, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt"
                ).to(self.model.device, dtype=torch.bfloat16)
                
                input_len = inputs["input_ids"].shape[-1]

                with torch.inference_mode():
                    generation = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens)
                    generation = generation[0][input_len:]

                response = self.processor.decode(
                    generation, skip_special_tokens=True
                )

                reasoning_content, completion_token_count, reasoning_token_count, total_token_count = self.get_model_stats(response, input_len)

                return response, data + [{"role": "assistant", "content": [{"type": "text", "text": response}]}], reasoning_content, completion_token_count, reasoning_token_count, total_token_count
            else:
                data, message_list = self.process_text_message(message_data, with_history)

                inputs = self.processor.apply_chat_template(
                    message_list, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt"
                ).to(self.model.device, dtype=torch.bfloat16)
                
                input_len = inputs["input_ids"].shape[-1]

                with torch.inference_mode():
                    generation = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens)
                    generation = generation[0][input_len:]

                response = self.processor.decode(
                    generation, skip_special_tokens=True
                )

                reasoning_content, completion_token_count, reasoning_token_count, total_token_count = self.get_model_stats(response, input_len)

                return response, data + [{"role": "assistant", "content": [{"type": "text", "text": response}]}], reasoning_content, completion_token_count, reasoning_token_count, total_token_count
        
        elif 'llama' in self.name.lower():
            data, message_list = self.process_text_message(message_data, with_history)

            response = self.model(message_list, max_new_tokens=self.max_new_tokens)

            # calculate input tokens
            input_text = self.tokenizer.apply_chat_template(message_list, tokenize=False)
            input_tokens = self.tokenizer(input_text, return_tensors="pt")

            reasoning_content, completion_token_count, reasoning_token_count, total_token_count = self.get_model_stats(response, input_tokens.input_ids.shape[1])
            return response[0]["generated_text"][-1]["content"], data + [{"role": "assistant", "content": response[0]["generated_text"][-1]["content"]}], reasoning_content, completion_token_count, reasoning_token_count, total_token_count

        elif 'qwq' in self.name.lower():
            data, message_list = self.process_text_message(message_data, with_history)

            text = self.tokenizer.apply_chat_template(
                message_list,
                tokenize=False,
                add_generation_prompt=True,
            )

            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=32768
            )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]

            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

            reasoning_content, completion_token_count, reasoning_token_count, total_token_count = self.get_model_stats(generated_ids, model_inputs.input_ids.shape[1])

            return response.split('</think>')[1], data + [{"role": "assistant", "content": response.split('</think>')[1]}], reasoning_content, completion_token_count, reasoning_token_count, total_token_count

        elif 'qwen' in self.name.lower():
            if type(message_data) == list:
                data, message_list = self.process_multimodal_message(message_data, with_history)
        
                # Preparation for inference
                text = self.processor.apply_chat_template(
                    message_list, tokenize=False, add_generation_prompt=True
                )
                image_inputs, video_inputs = process_vision_info(message_list)
                inputs = self.processor(
                    text=[text],
                    images=image_inputs,
                    videos=video_inputs,
                    padding=True,
                    return_tensors="pt",
                )
                inputs = inputs.to("cuda")

                # Inference: Generation of the output
                generated_ids = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens)
                generated_ids_trimmed = [
                    out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
                ]
                response = self.processor.batch_decode(
                    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
                )[0]

                reasoning_content, completion_token_count, reasoning_token_count, total_token_count = self.get_model_stats(response, inputs.input_ids.shape[1])

                return response, data + [{"role": "assistant", "content": [{"type": "text", "text": response}]}], reasoning_content, completion_token_count, reasoning_token_count, total_token_count
            else:
                data, message_list = self.process_text_message(message_data, with_history)

                # Preparation for inference
                text = self.processor.apply_chat_template(
                    message_list, tokenize=False, add_generation_prompt=True
                )
                image_inputs, video_inputs = process_vision_info(message_list)
                inputs = self.processor(
                    text=[text],
                    images=image_inputs,
                    videos=video_inputs,
                    padding=True,
                    return_tensors="pt",
                )
                inputs = inputs.to("cuda")

                # Inference: Generation of the output
                generated_ids = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens)
                generated_ids_trimmed = [
                    out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
                ]

                response = self.processor.batch_decode(
                    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
                )[0]

                reasoning_content, completion_token_count, reasoning_token_count, total_token_count = self.get_model_stats(response, inputs.input_ids.shape[1])
                return response, data + [{"role": "assistant", "content": [{"type": "text", "text": response}]}], reasoning_content, completion_token_count, reasoning_token_count, total_token_count
        
        elif 'phi' in self.name.lower():
            if type(message_data) == list:
                data, message_list = self.process_multimodal_message(message_data, with_history)
        
                response = phi_client.complete(
                    messages=message_list,
                    max_tokens=self.max_new_tokens,
                    model="Phi-4-multimodal-instruct"
                )

                reasoning_content, completion_token_count, reasoning_token_count, total_token_count = self.get_model_stats(response, None)

                return response.choices[0].message.content, data + [AssistantMessage(content=response.choices[0].message.content)], reasoning_content, completion_token_count, reasoning_token_count, total_token_count
            else:
                data, message_list = self.process_text_message(message_data, with_history)

                response = phi_client.complete(
                    messages=message_list,
                    max_tokens=self.max_new_tokens,
                    model="Phi-4-multimodal-instruct"
                )

                reasoning_content, completion_token_count, reasoning_token_count, total_token_count = self.get_model_stats(response, None)

                return response.choices[0].message.content, data + [AssistantMessage(content=response.choices[0].message.content)], reasoning_content, completion_token_count, reasoning_token_count, total_token_count

    def get_formated_history(self, with_history: bool) -> List[dict]:
        unified_history = []
        input_counts = []  # To store input token counts for user messages

        # Process history in pairs (user, assistant)
        for i in range(0, len(self.history), 2):
            user_message = self.history[i] if i < len(self.history) else None
            assistant_message = self.history[i + 1] if i + 1 < len(self.history) else None
            token_idx = i // 2  # Index for token lists (since tokens correspond to assistant responses)

            # Process user message
            if user_message:
                role = None
                content = None
                reasoning_content = None
                reasoning_count = 0
                content_count = 0  # Default, will calculate if token info available

                # Extract role and content based on model-specific format
                if self.name.lower() in ['gpt-4.1', 'o4-mini', 'grok-3-mini-beta', 'deepseek-reasoner', 'deepseek-chat', 'qwq', 'llama', 'gemma', 'qwen']:
                    if isinstance(user_message, dict) and 'role' in user_message:
                        role = user_message['role']
                        if role == 'system':
                            role = 'user'
                        if role in ['user', 'system']:
                            if isinstance(user_message['content'], str):
                                content = user_message['content']
                            elif isinstance(user_message['content'], list):
                                content = ''
                                for item in user_message['content']:
                                    if item['type'] == 'text':
                                        content += item['text']
                                    else:
                                        # add image placeholder
                                        content += '<image>'
                            else:
                                content = str(user_message['content'])
                    else:
                        role = 'user'
                        content = str(user_message)

                elif self.name.lower() == 'gemini-2.5-pro-preview-03-25':
                    role = 'user'
                    content = ''
                    for p in user_message.parts:
                        if p.text is not None:
                            content += p.text
                        else:
                            # add image placeholder
                            content += '<image>'

                elif 'phi' in self.name.lower():
                    if isinstance(user_message, (SystemMessage, UserMessage)):
                        role = 'user'
                        content_items = user_message.content
                        try:
                            content_items = eval(content_items)
                            content = ''
                            for item in content_items:
                                if 'text' in item:
                                    content += item['text']
                                else:
                                    # add image placeholder
                                    content += '<image>'
                        except Exception as e:
                            content = str(user_message)
                    else:
                        role = 'user'
                        content = str(user_message)

                if with_history:
                    # Estimate content_count for user message
                    if token_idx < len(self.completion_tokens):
                        # Use total_token_count from assistant response if available
                        total_token_count = self.total_tokens[token_idx] if token_idx < len(self.total_tokens) and self.total_tokens[token_idx] is not None else 0
                        completion_count = self.completion_tokens[token_idx] if token_idx < len(self.completion_tokens) and self.completion_tokens[token_idx] is not None else 0
                        reasoning_count_assistant = self.reasoning_tokens[token_idx] if token_idx < len(self.reasoning_tokens) and self.reasoning_tokens[token_idx] is not None else 0
                        input_count = total_token_count - (reasoning_count_assistant + completion_count) - sum(self.completion_tokens[:token_idx]) - sum(input_counts)
                        content_count = max(input_count, 0)  # Ensure non-negative
                        input_counts.append(content_count)
                    else:
                        input_counts.append(0)
                else:
                    if token_idx < len(self.completion_tokens):
                        # Use total_token_count from assistant response if available
                        total_token_count = self.total_tokens[token_idx] if token_idx < len(self.total_tokens) else 0
                        completion_count = self.completion_tokens[token_idx] if token_idx < len(self.completion_tokens) and self.completion_tokens[token_idx] is not None else 0
                        reasoning_count_assistant = self.reasoning_tokens[token_idx] if token_idx < len(self.reasoning_tokens) else 0
                        content_count = total_token_count - (reasoning_count_assistant + completion_count)

                unified_history.append({
                    'role': role,
                    'reasoning_content': reasoning_content,
                    'reasoning_count': reasoning_count,
                    'content': content,
                    'content_count': content_count
                })

            # Process assistant message
            if assistant_message:
                role = None
                content = None
                reasoning_content = self.reasoning[token_idx] if token_idx < len(self.reasoning) else None
                reasoning_count = self.reasoning_tokens[token_idx] if token_idx < len(self.reasoning_tokens) else 0
                content_count = self.completion_tokens[token_idx] if token_idx < len(self.completion_tokens) else 0

                # Extract role and content based on model-specific format
                if self.name.lower() in ['gpt-4.1', 'o4-mini', 'grok-3-mini-beta', 'deepseek-reasoner', 'deepseek-chat', 'qwq', 'llama', 'gemma', 'qwen']:
                    if isinstance(assistant_message, dict) and 'role' in assistant_message:
                        role = assistant_message['role']
                        if role == 'assistant':
                            if isinstance(assistant_message['content'], str):
                                content = assistant_message['content']
                            elif isinstance(assistant_message['content'], list):
                                content = ''
                                for item in assistant_message['content']:
                                    if item['type'] == 'text':
                                        content += item['text']
                            else:
                                content = str(assistant_message['content'])
                    else:
                        role = 'assistant'
                        content = str(assistant_message)

                elif self.name.lower() == 'gemini-2.5-pro-preview-03-25':
                    role = assistant_message.role
                    if role == 'model':
                        role = 'assistant'
                    
                    content = ''
                    for p in assistant_message.parts:
                        if p.text is not None:
                            content += p.text

                elif 'phi' in self.name.lower():
                    if isinstance(assistant_message, AssistantMessage):
                        role = 'assistant'
                        content = assistant_message.content
                    else:
                        role = 'assistant'
                        content = str(assistant_message)

                unified_history.append({
                    'role': role,
                    'reasoning_content': reasoning_content,
                    'reasoning_count': reasoning_count,
                    'content': content,
                    'content_count': content_count
                })

        return unified_history


    def get_raw_output4simulator(self) -> List[BaseMessageDataType]:
        return None
    
    def receive_message(self, message: Info) -> Info:
        return None

    def clear(self):
        self.images = []
        self.history = []
        self.completion_tokens = []
        self.reasoning = []
        self.reasoning_tokens = []
        self.total_tokens = []
        self.total_usage = 0