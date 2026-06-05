@extends('base')

@section('title', ucfirst($form_type) . ' Form')

@section('content')
<div class="max-w-2xl mx-auto">
    <div class="card">
        <h2 class="text-3xl font-bold mb-6">{{ ucfirst($form_type) }} Form</h2>

        <form method="POST" action="{{ route('form.submit') }}" enctype="multipart/form-data" id="submitForm">
            @csrf

            <input type="hidden" name="form_type" value="{{ $form_type }}">

            @foreach($formData as $fieldName => $field)
                <div class="mb-6">
                    <label class="block text-gray-700 font-semibold mb-2">
                        {{ $field['label'] }}
                        @if($field['required'] ?? false)
                            <span class="text-red-600">*</span>
                        @endif
                    </label>

                    @if($field['type'] === 'text' || $field['type'] === 'email' || $field['type'] === 'tel' || $field['type'] === 'number')
                        <input 
                            type="{{ $field['type'] }}" 
                            name="{{ $fieldName }}"
                            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            {{ ($field['required'] ?? false) ? 'required' : '' }}
                            value="{{ old($fieldName) }}"
                        >

                    @elseif($field['type'] === 'date')
                        <input 
                            type="date" 
                            name="{{ $fieldName }}"
                            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            {{ ($field['required'] ?? false) ? 'required' : '' }}
                            value="{{ old($fieldName) }}"
                        >

                    @elseif($field['type'] === 'file')
                        <input 
                            type="file" 
                            name="{{ $fieldName }}"
                            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            {{ ($field['required'] ?? false) ? 'required' : '' }}
                        >

                    @elseif($field['type'] === 'textarea')
                        <textarea 
                            name="{{ $fieldName }}"
                            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            rows="5"
                            {{ ($field['required'] ?? false) ? 'required' : '' }}
                        >{{ old($fieldName) }}</textarea>

                    @elseif($field['type'] === 'select')
                        <select 
                            name="{{ $fieldName }}"
                            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            {{ ($field['required'] ?? false) ? 'required' : '' }}
                        >
                            <option value="">-- Select an option --</option>
                            @if(isset($field['options']))
                                @foreach($field['options'] as $option)
                                    <option value="{{ $option }}" {{ old($fieldName) == $option ? 'selected' : '' }}>
                                        {{ $option }}
                                    </option>
                                @endforeach
                            @endif
                        </select>

                    @endif

                    @error($fieldName)
                        <span class="text-red-600 text-sm">{{ $message }}</span>
                    @enderror
                </div>
            @endforeach

            <div class="flex gap-4 mt-8">
                <button 
                    type="submit" 
                    class="btn-primary flex-1"
                >
                    <i class="fas fa-check"></i> Submit Form
                </button>
                <a href="{{ route('home') }}" class="btn-secondary flex-1 text-center">
                    <i class="fas fa-times"></i> Cancel
                </a>
            </div>
        </form>
    </div>
</div>

@section('extra-js')
<script>
    document.getElementById('submitForm').addEventListener('submit', function(e) {
        if (!confirm('Are you sure you want to submit this form?')) {
            e.preventDefault();
        }
    });
</script>
@endsection

@endsection
