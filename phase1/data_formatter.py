"""
Data Formatter for LLM Fine-Tuning
Converts raw data into instruction format (Alpaca or ChatML)
"""

import jsonlines
from typing import List, Dict, Optional
from pathlib import Path


class DataFormatter:
    """Handles conversion of various data formats to instruction format"""
    
    ALPACA_PROMPT = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{input}

### Response:
{output}"""

    ALPACA_PROMPT_NO_INPUT = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:
{output}"""

    @staticmethod
    def format_alpaca(
        instruction: str,
        output: str,
        input_text: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Format a single example into Alpaca format
        
        Args:
            instruction: The task instruction
            output: The expected output/response
            input_text: Optional context or input
            
        Returns:
            Dictionary with 'text' key containing formatted prompt
        """
        if input_text and input_text.strip():
            text = DataFormatter.ALPACA_PROMPT.format(
                instruction=instruction,
                input=input_text,
                output=output
            )
        else:
            text = DataFormatter.ALPACA_PROMPT_NO_INPUT.format(
                instruction=instruction,
                output=output
            )
        
        return {"text": text}
    
    @staticmethod
    def format_chatml(
        instruction: str,
        output: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Format a single example into ChatML format
        
        Args:
            instruction: The user message
            output: The assistant response
            system_prompt: Optional system message
            
        Returns:
            Dictionary with 'text' key containing formatted conversation
        """
        messages = []
        
        if system_prompt:
            messages.append(f"<|im_start|>system\n{system_prompt}<|im_end|>")
        
        messages.append(f"<|im_start|>user\n{instruction}<|im_end|>")
        messages.append(f"<|im_start|>assistant\n{output}<|im_end|>")
        
        text = "\n".join(messages)
        return {"text": text}
    
    @staticmethod
    def load_and_format_jsonl(
        input_path: str,
        format_type: str = "alpaca",
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Load JSONL file and format all entries
        
        Expected JSONL format:
        {"instruction": "...", "output": "...", "input": "..." (optional)}
        
        Args:
            input_path: Path to input JSONL file
            format_type: Either 'alpaca' or 'chatml'
            system_prompt: Optional system prompt for ChatML format
            
        Returns:
            List of formatted examples
        """
        formatted_data = []
        
        with jsonlines.open(input_path) as reader:
            for obj in reader:
                instruction = obj.get("instruction", "")
                output = obj.get("output", "")
                input_text = obj.get("input", "")
                
                if not instruction or not output:
                    continue
                
                if format_type == "alpaca":
                    formatted = DataFormatter.format_alpaca(
                        instruction, output, input_text
                    )
                elif format_type == "chatml":
                    formatted = DataFormatter.format_chatml(
                        instruction, output, system_prompt
                    )
                else:
                    raise ValueError(f"Unknown format type: {format_type}")
                
                formatted_data.append(formatted)
        
        return formatted_data
    
    @staticmethod
    def save_formatted_data(
        data: List[Dict[str, str]],
        output_path: str
    ) -> None:
        """
        Save formatted data to JSONL file
        
        Args:
            data: List of formatted examples
            output_path: Path to save output file
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with jsonlines.open(output_path, mode='w') as writer:
            writer.write_all(data)
        
        print(f"✓ Saved {len(data)} formatted examples to {output_path}")


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Format data for LLM fine-tuning")
    parser.add_argument("--input", required=True, help="Input JSONL file")
    parser.add_argument("--output", required=True, help="Output JSONL file")
    parser.add_argument(
        "--format",
        default="alpaca",
        choices=["alpaca", "chatml"],
        help="Output format"
    )
    parser.add_argument("--system", help="System prompt (for ChatML)")
    
    args = parser.parse_args()
    
    data = DataFormatter.load_and_format_jsonl(
        args.input,
        args.format,
        args.system
    )
    DataFormatter.save_formatted_data(data, args.output)
