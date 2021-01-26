import React from 'react'
import './index.scss'

export interface RadioOption {
    key: string
    label: string
    icon?: any // any, because Ant Design icons are some weird ForwardRefExoticComponent type
}

interface RadioOptionProps {
    options: RadioOption[]
    selectedOption?: null | string
    onOptionChanged: (key: string | null) => void
}

export function RadioOption({ options, selectedOption, onOptionChanged }: RadioOptionProps): JSX.Element {
    return (
        <div className="ph-radio-options">
            {options.map((option) => (
                <div
                    className={`radio-option${selectedOption === option.key ? ' active' : ''}`}
                    key={option.key}
                    onClick={() => onOptionChanged(selectedOption !== option.key ? option.key : null)}
                >
                    <div className="graphic">{option.icon}</div>
                    <div className="label">{option.label}</div>
                </div>
            ))}
        </div>
    )
}